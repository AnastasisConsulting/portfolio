"""
Copyright (c) 2025 William Wallace
G-Synthetic Project

Usage of this code is subject to the MIT license + G-Synthetic Addendum + Patent Notice.
See LICENSE file for full terms.
"""

import json
import re
import os
import sys
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Iterable, Union
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import logging
import datetime

# Your LLMManager is the main entry point for LLM interactions
from llm_tank.llm_core import LLMManager
# Your memory and timeline utilities
from .memory import write_memory_from_reply, read_memory_for_prompt
from .timeline_store import next_page_for, save_x_up, save_y_up
from PySide6.QtCore import QObject
# Base CPU class, used for the fallback and by the CoralEncoder for tokenization
from sentence_transformers import SentenceTransformer

# --- NEW: game_types.py content integrated here for clarity ---

# Forward declaration for type hints within classes
class StarLore: pass
class PlanetLore: pass

@dataclass
class LoreEntry:
    id: str
    name: str
    baseLore: str
    discovered: bool = False

@dataclass
class GalaxyLore(LoreEntry):
    stars: Dict[str, StarLore] = field(default_factory=dict)

@dataclass
class StarLore(LoreEntry):
    planets: Dict[str, PlanetLore] = field(default_factory=dict)

@dataclass
class PlanetLore(LoreEntry):
    # Add other planet-specific fields as needed
    pass

@dataclass
class LorebookData:
    galaxies: Dict[str, GalaxyLore] = field(default_factory=dict)
    # bleed: Dict[str, BleedLore] = field(default_factory=dict) # Can be added later

@dataclass
class JournalEntry:
    id: str
    title: str
    description: str
    status: str # 'active' or 'completed'

@dataclass
class Character:
    id: str
    name: str
    isPlayer: bool
    # Add other character fields as needed

@dataclass
class CampaignState:
    currentMissionId: str
    discoveredFragments: List[str] = field(default_factory=list)

@dataclass
class StoryFractalCoordinates:
    plotPoints: int
    drivers: int
    sideQuests: int

@dataclass
class ContextGridNode:
    id: str
    type: str # 'lore', 'character', 'journal', etc.
    content: Any

# This will represent the full game state passed to the context builder
@dataclass
class GameData:
    lorebook: LorebookData
    currentLocationId: Optional[str]
    characters: List[Character]
    journal: List[JournalEntry]
    campaignState: Optional[CampaignState]
    storyFractalCoordinates: Optional[StoryFractalCoordinates]
    reputation: Dict[str, int]
# --- END NEW ---

def _triad_sign(x: float) -> int:
    """Maps a score from [-3, 3] to -1, 0, or 1."""
    if x > 0.15: return 1
    if x < -0.15: return -1
    return 0

# --- 1. MEMORY & FILE SYSTEM MANAGEMENT ---
MEMORY_DIR = "game_data/memory"
SCAFFOLDING_FILE = os.path.join(MEMORY_DIR, "narrative_scaffolding.json")
LIBRARY_DIR = os.path.join(MEMORY_DIR, "hypercube_library")

RHETORICAL_ARCS = ("essence", "form", "action", "frame", "intent", "relation", "value")
MACRO_PHASES = ("Input", "Identity", "Inception")
TRANSFORMS = ["Characters", "GeoMemory", "Story"]
TRANSFORM_INDEX = {name: i for i, name in enumerate(TRANSFORMS)}
MODIFIERS = {
    "Characters": ["MainCharacter", "CoStars", "NPCs"],
    "GeoMemory":  ["WorldState", "Factions", "ForcesAtPlay"],
    "Story":      ["Setup", "Confrontation", "Resolution"],
}
MOD_INDEX = {t: {m: i for i, m in enumerate(mods)} for t, mods in MODIFIERS.items()}
ARCS = ["Essence", "Form", "Function", "Context", "Intent", "Relation", "Value"]
ARC_INDEX = {name: i for i, name in enumerate(ARCS)}
# The 7 rhetorical arcs (fixed order → deterministic tic indices)

# --- DATA CLASSES & HELPERS ---
@dataclass
class RhetoricalArcs:
    essence: str = ""
    form: str = ""
    action: str = ""
    frame: str = ""
    intent: str = ""
    relation: str = ""
    value: str = ""

class SimpleVectorIndex:
    def __init__(self):
        self.vectors = []
        self.metadata = []

    def add(self, vector: np.ndarray, meta: dict):
        self.vectors.append(vector)
        self.metadata.append(meta)

    def search(self, query_vector: np.ndarray, top_k: int) -> List[dict]:
        if not self.vectors:
            return []
        index_matrix = np.array(self.vectors)
        sims = np.dot(index_matrix, query_vector)
        top_k_indices = np.argsort(sims)[-top_k:][::-1]
        return [self.metadata[i] for i in top_k_indices]

# --- TEMPLATE MANAGEMENT ---
class TemplateLoader:
    def __init__(self, character: str, base_dir: str = "main_app/engine/templates"):
        self.base_dir = Path(base_dir)
        self.filepath = self._get_filepath(character)

    def _get_filepath(self, character: str) -> Path:
        if character.lower() == "emily":
            return self.base_dir / "geo_char_story_template.json"
        return self.base_dir / "default_transform_template.json"

    def load(self) -> Dict:
        if not self.filepath.exists():
            raise FileNotFoundError(f"Template file not found: {self.filepath}")
        with self.filepath.open("r") as f:
            return json.load(f)

class ModifierMatrix:
    def __init__(self, template_data: Dict):
        self.grid: List[List[List[str]]] = self._build_matrix(template_data)

    def _build_matrix(self, data: Dict) -> List[List[List[str]]]:
        matrix = []
        transforms = data.get("transforms", [])
        if isinstance(transforms, dict): transforms = list(transforms.values())
        for transform in transforms:
            row = []
            modifiers = transform.get("modifiers", [])
            if isinstance(modifiers, dict): modifiers = list(modifiers.values())
            for modifier in modifiers:
                row.append(modifier.get("elements", []))
            matrix.append(row)
        return matrix

    def get_element(self, phase_index: int, mod_index: int, rank_index: int) -> str:
        try:
            elements = self.grid[phase_index][mod_index]
            index = rank_index - 1
            if 0 <= index < len(elements): return elements[index]
            return "[Missing Element]"
        except IndexError:
            return "[Missing Element]"

# --- LLM AGENT PROMPTS ---
DECOMPOSITION_PROMPT = """
You are a master of symbolic decomposition...

Input: "{player_input}"
Output:
"""

SYNTHESIS_PROMPT = """
You are a master storyteller and game master for the game Eideus Dawn...

# Example Input
Player's Action: "I look at the bartender."
Memory Coordinate: "x0-y2-z0"

# Example Output
{{
  "narrative": "You turn your attention to the bartender, a burly man with a weary expression. He pauses his work, wiping a mug with a stained rag, and meets your gaze with a hint of curiosity.",
  "character_aspect": "This action marks your first conscious decision to engage with another person.",
  "world_aspect": "The bartender is established as a key figure in this immediate environment.",
  "story_aspect": "An opportunity for dialogue and information gathering has been created.",
  "ascii_map": "#########################\\n#        B              #\\n#       ---             #\\n#      |   |            #\\n#                       #\\n#   @                   #\\n#                       #\\n#                       #\\n#                       #\\n#                       #\\n#                       #\\n#########################"
}}

{memory_context}
# Deconstructed Player Action
{arc_context}

# Player's Raw Action
"{player_input}"

# Memory Coordinate (Where this event will be stored)
"{coordinate_string}"

# Output
"""

# --- DETERMINISTIC ROUTERS ---
WORLD_LOCAL = {"bar", "door", "corner", "stool", "table", "window", "floor", "lantern", "stairs", "kitchen"}
WORLD_FACTION = {"rule", "tax", "guard", "guild", "order", "law", "barkeep", "owner", "patronage", "faction", "taboo"}
STORY_SETUP = {"wake", "begin", "arrive", "enter", "new", "first", "learn"}
STORY_CONFLICT = {"threat", "fight", "argue", "refuse", "block", "danger", "chase", "pursue", "steal", "attack"}
STORY_RESOLVE = {"solve", "accept", "agree", "end", "leave", "escape", "resolve", "finish"}
SELF_WORDS = {"i", "me", "my", "myself"}

def route_transform(player_text: str) -> int:
    t = player_text.lower()
    if any(w in t for w in STORY_CONFLICT) or any(w in t for w in STORY_RESOLVE):
        return TRANSFORM_INDEX["Story"]
    if any(w in t for w in WORLD_LOCAL) or any(w in t for w in WORLD_FACTION):
        return TRANSFORM_INDEX["GeoMemory"]
    return TRANSFORM_INDEX["Characters"]

def route_modifier(t_idx: int, player_text: str, mentioned_names: List[str]) -> int:
    tname = TRANSFORMS[t_idx]
    t = player_text.lower()
    if tname == "Characters":
        if any(w in t for w in SELF_WORDS):
            return MOD_INDEX["Characters"]["MainCharacter"]
        if mentioned_names:
            return MOD_INDEX["Characters"]["CoStars"]
        return MOD_INDEX["Characters"]["NPCs"]
    if tname == "GeoMemory":
        if any(w in t for w in WORLD_FACTION):
            return MOD_INDEX["GeoMemory"]["Factions"]
        if any(w in t for w in WORLD_LOCAL):
            return MOD_INDEX["GeoMemory"]["ForcesAtPlay"]
        return MOD_INDEX["GeoMemory"]["WorldState"]
    if tname == "Story":
        if any(w in t for w in STORY_CONFLICT):
            return MOD_INDEX["Story"]["Confrontation"]
        if any(w in t for w in STORY_RESOLVE):
            return MOD_INDEX["Story"]["Resolution"]
        if any(w in t for w in STORY_SETUP):
            return MOD_INDEX["Story"]["Setup"]
        return MOD_INDEX["Story"]["Setup"]
    return 0

def route_tic(dominant_arc: str) -> int:
    return RHETORICAL_ARCS.index(dominant_arc) if dominant_arc in RHETORICAL_ARCS else 0

class FractalMemoryEngine(QObject):
    """
    The main orchestrator, handling all LLM, encoder, and memory interactions.
    """
    def __init__(self, llm_manager: "LLMManager", character: str = "default", use_memory: bool = True):
        super().__init__()
        self.llm_manager = llm_manager
        self.character = character
        self.use_memory = use_memory
        
        # --- NEW: Initialize full game state attributes ---
        self.lorebook = LorebookData()
        self.current_location_id: Optional[str] = None
        self.journal: List[JournalEntry] = []
        self.campaign_state: Optional[CampaignState] = None
        self.story_fractal_coordinates: Optional[StoryFractalCoordinates] = None
        self.reputation: Dict[str, int] = {}
        self.game_characters: List[Character] = []
        
        # Encoder is always needed for some logic, even if memory is off
        self.encoder = initialize_encoder()
        
        # --- MEMORY TOGGLE: Conditionally initialize all memory components ---
        if self.use_memory:
            print("[Engine] Memory system ENABLED.")
            self.store = LatticeMemoryStore()
            self.vector_index = SimpleVectorIndex()
            self.main_char_id: str = "MC"
            self.characters: Dict[str, Dict[str, Any]] = {
                self.main_char_id: {"name": "Player", "embedding": None, "parent": None}
            }
            self.supporting_ids: List[str] = []
            self.relationships: Dict[tuple, float] = {}
        else:
            print("[Engine] Memory system DISABLED.")
            self.store = None
            self.vector_index = None
            self.main_char_id: str = "MC"
            self.characters = {}
            self.supporting_ids = []
            self.relationships = {}
        
        self.turn_cache: List[Dict[str, Any]] = []
        self.current_chapter_num: int = 1

    def _call_llm_agent(self, agent_prompt: str, **kwargs) -> str:
        """Robustly calls the active LLM and returns the cleaned text response."""
        active_llm = self.llm_manager.get_active_llm()
        if not active_llm or not active_llm.is_loaded:
            print("\n--- LLM AGENT FAILED: No active LLM loaded. ---")
            return json.dumps({"narrative": "Error: LLM not available."})
        
        final_prompt = agent_prompt.format(**kwargs)
        
        print("\n" + "="*50)
        print(f"--- Calling LLM Agent: {active_llm.get_name()} ---")
        print(f"--- PROMPT START ---\n{final_prompt}\n--- PROMPT END ---")
        
        try:
            response_text = active_llm.generate_response(prompt=final_prompt, history=[], hyperparameters={})
            print(f"--- RAW LLM RESPONSE ---\n{response_text}\n" + "="*50 + "\n")
        except Exception as e:
            logging.error(f"LLM generation failed: {e}")
            return json.dumps({"narrative": f"Error during LLM call: {e}"})

        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        return match.group(0) if match else response_text

    def run_turn(self, player_input: str) -> Dict:
        """Main processing pipeline for a user turn."""
        print(f"\n>>> PLAYER INPUT: \"{player_input}\"")

        # 1) Decompose input
        decomposed_arcs_str = self._call_llm_agent(DECOMPOSITION_PROMPT, player_input=player_input)
        try:
            decomposed_arcs_dict = json.loads(decomposed_arcs_str)
        except json.JSONDecodeError as e:
            print(f"\n--- JSON PARSING ERROR: {e} ---")
            return {"narrative": "Error: Failed to parse LLM decomposition."}

        # 2) Token counts & Dominant Arc
        arc_token_counts = {arc: len(decomposed_arcs_dict.get(arc, "").split()) for arc in RHETORICAL_ARCS}
        if not arc_token_counts:
            dominant_arc = "essence" # Default fallback
        else:
            dominant_arc = max(arc_token_counts, key=lambda k: arc_token_counts.get(k, 0))
        
        # 3) Coordinate Routing & Character Detection
        mentioned_texts = self._detect_characters(player_input)
        t_idx = route_transform(player_input)
        m_idx = route_modifier(t_idx, player_input, mentioned_texts)
        e_idx = route_tic(dominant_arc)
        coord_str = f"x{t_idx}-y{m_idx}-z{e_idx}"
        
        arc_context = "\n".join(
            f'- {arc.capitalize()}: {decomposed_arcs_dict.get(arc, "N/A")} (Magnitude: {arc_token_counts.get(arc, 0)})'
            for arc in RHETORICAL_ARCS
        )

        # 4) Memory Operations (MODIFIED)
        context_grid = self._build_context_grid()
        memory_context = self._format_context_grid_for_prompt(context_grid)
        
        if self.use_memory and self.vector_index:
            mentioned_ids: List[str] = [self._link_character(m) for m in mentioned_texts]
            self._score_interaction(self.main_char_id, mentioned_ids, player_input)
            self._update_supporting_parentage(mentioned_ids)
            self._maybe_promote_or_demote()

            embedding_result = self.encoder.encode(player_input)
            input_embedding = np.asarray(embedding_result)

            event_meta = {"coord": coord_str, "input": player_input, "arc": dominant_arc}
            self.vector_index.add(input_embedding, event_meta)
            
            recalled_events = self.recall_similar_events(player_input)
            if recalled_events:
                memory_context += "\n# Relevant Past Events (for context):\n"
                for event in recalled_events:
                    if event["coord"] != coord_str:
                        memory_context += f'- Previously at {event["coord"]}, you did this: "{event["input"]}"\n'
        
        # 5) Synthesis
        response_json_str = self._call_llm_agent(
            SYNTHESIS_PROMPT,
            player_input=player_input,
            coordinate_string=coord_str,
            arc_context=arc_context,
            memory_context=memory_context
        )
        
        try:
            synthesized_data = json.loads(response_json_str)
        except json.JSONDecodeError:
            synthesized_data = {"narrative": "The world feels hazy and indistinct...", "error": "synthesis_parse_fail"}

        # 6) Build event and conditionally write-through to lattice node
        if self.use_memory and self.store:
            event = {
                "coord": coord_str,
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "player_input": player_input,
                "arcs": decomposed_arcs_dict,
                "synthesis": synthesized_data
            }
            self.turn_cache.append(event)
            self.store.write_entry(coord_str, event)
            print(f"Filed memory at {coord_str}")

        final_output = {"coordinate": coord_str}
        final_output.update(synthesized_data)
        return final_output
    
    # --- NEW HELPER METHOD ---
    def _coord_to_index(self, x: int, y: int, z: int) -> int:
        """Converts 3D coordinates (0-6) to a 1D array index."""
        if not (0 <= x <= 6 and 0 <= y <= 6 and 0 <= z <= 6):
            return -1
        return x + y * 7 + z * 49

    # --- NEW METHOD ---
    def _build_context_grid(self) -> List[Optional[ContextGridNode]]:
        """Builds a 7x7x7 context grid centered on the player's current location."""
        grid: List[Optional[ContextGridNode]] = [None] * 343
        
        game_data = GameData(
            lorebook=self.lorebook,
            currentLocationId=self.current_location_id,
            characters=self.game_characters,
            journal=self.journal,
            campaignState=self.campaign_state,
            storyFractalCoordinates=self.story_fractal_coordinates,
            reputation=self.reputation,
        )

        if not game_data.currentLocationId:
            return grid

        current_planet: Optional[PlanetLore] = None
        current_star: Optional[StarLore] = None
        current_galaxy: Optional[GalaxyLore] = None

        for galaxy in game_data.lorebook.galaxies.values():
            for star in galaxy.stars.values():
                if game_data.currentLocationId in star.planets:
                    current_planet = star.planets[game_data.currentLocationId]
                    current_star = star
                    current_galaxy = galaxy
                    break
            if current_planet:
                break
        
        if not current_planet:
            return grid

        player = next((c for c in game_data.characters if c.isPlayer), None)
        active_quests = [j for j in game_data.journal if j.status == 'active']

        grid[self._coord_to_index(3, 3, 3)] = ContextGridNode(id=current_planet.id, type='lore', content=current_planet)
        
        if current_star:
            grid[self._coord_to_index(3, 3, 2)] = ContextGridNode(id=current_star.id, type='lore', content=current_star)
        if current_galaxy:
            grid[self._coord_to_index(3, 3, 4)] = ContextGridNode(id=current_galaxy.id, type='lore', content=current_galaxy)
        if active_quests:
            grid[self._coord_to_index(3, 2, 3)] = ContextGridNode(id=active_quests[0].id, type='journal', content=active_quests[0])
        if player:
            grid[self._coord_to_index(2, 3, 3)] = ContextGridNode(id=player.id, type='character', content=player)
        
        if current_star:
            sibling_planets = [p for p in current_star.planets.values() if p.id != current_planet.id]
            if len(sibling_planets) > 0:
                grid[self._coord_to_index(4, 3, 3)] = ContextGridNode(id=sibling_planets[0].id, type='lore', content=sibling_planets[0])
            if len(sibling_planets) > 1:
                grid[self._coord_to_index(3, 4, 3)] = ContextGridNode(id=sibling_planets[1].id, type='lore', content=sibling_planets[1])

        if game_data.campaignState:
            content = {
                "currentMissionId": game_data.campaignState.currentMissionId,
                "discoveredFragments": len(game_data.campaignState.discoveredFragments)
            }
            grid[self._coord_to_index(2, 2, 2)] = ContextGridNode(id='campaign_state', type='campaign', content=content)
        
        if game_data.reputation:
            grid[self._coord_to_index(4, 4, 4)] = ContextGridNode(id='reputation_summary', type='reputation', content=game_data.reputation)
            
        if game_data.storyFractalCoordinates:
            grid[self._coord_to_index(1, 1, 1)] = ContextGridNode(id='story_fractal', type='story', content=game_data.storyFractalCoordinates)

        return grid

    # --- NEW HELPER METHOD ---
    def _format_context_grid_for_prompt(self, grid: List[Optional[ContextGridNode]]) -> str:
        """Formats the context grid into a string for the LLM prompt."""
        prompt_lines = ["**SITUATIONAL CONTEXT GRID (Player is at the center [P]):**"]
        added_ids = set()

        def process_node(node: Optional[ContextGridNode], label: str):
            if node and node.id not in added_ids:
                content_summary = f"{node.content.name}: {node.content.baseLore}" if isinstance(node.content, LoreEntry) else str(node.content)
                prompt_lines.append(f"- {label}: {content_summary}")
                added_ids.add(node.id)

        process_node(grid[self._coord_to_index(3, 3, 3)], "[P] Immediate Location")
        process_node(grid[self._coord_to_index(3, 3, 2)], "[P-1Z] Parent System")
        process_node(grid[self._coord_to_index(3, 3, 4)], "[P+1Z] Parent Galaxy")
        process_node(grid[self._coord_to_index(3, 2, 3)], "[P-1Y] Active Objective")
        return "\n".join(prompt_lines)

    def recall_similar_events(self, query: str, top_k: int = 5) -> List[Dict]:
        """Recall most similar past events using semantic embeddings."""
        if self.vector_index is None:
            print("No vector index initialized.")
            return []
            
        embedding_result = self.encoder.encode(query)
        query_embedding = np.asarray(embedding_result)
        
        return self.vector_index.search(query_embedding, top_k)
    
    def trigger_mutation(self) -> Dict:
        """Generates a spontaneous, surprising event."""
        print(">>> TRIGGERING STORY MUTATION...")
        mutation_prompt = "A surprising, unexpected event occurs in the tavern."
        coord_str = "mutation-event"
        
        response_json_str = self._call_llm_agent(
            SYNTHESIS_PROMPT,
            player_input=mutation_prompt,
            coordinate_string=coord_str,
            arc_context="Spontaneous event.",
            memory_context=""
        )
        try:
            return json.loads(response_json_str)
        except json.JSONDecodeError:
            return {"narrative": "A sudden silence falls over the tavern."}

    def flush_cache_to_file(self):
        """Write cached events to the chapter’s persistent JSON timeline."""
        if not self.use_memory or not self.turn_cache:
            return
        print(f"Flushed {len(self.turn_cache)} events.")
        self.turn_cache.clear()

    def _score_interaction(self, speaker_id: str, mentioned_ids: List[str], player_input: str) -> None:
        text = player_input.lower()
        pos_cues = ("thank", "smile", "help", "save", "ally", "gift", "apolog")
        neg_cues = ("hit", "steal", "threat", "insult", "betray", "kill", "attack")
        delta = 0.0
        if any(c in text for c in pos_cues): delta += 0.4
        if any(c in text for c in neg_cues): delta -= 0.6
        if delta == 0.0: delta = 0.1
        for mid in mentioned_ids:
            self._bump_rel(self.main_char_id, mid, delta)
            parent = self.characters.get(mid, {}).get("parent")
            if parent:
                self._bump_rel(self.main_char_id, parent, delta * 0.25)
                self._bump_rel(parent, mid, delta * 0.25)
        self._decay_relationships(0.01)

    def _rel_key(self, a: str, b: str) -> tuple:
        return (a, b) if a <= b else (b, a)

    def _bump_rel(self, a: str, b: str, delta: float) -> None:
        if a == b: return
        k = self._rel_key(a, b)
        self.relationships[k] = self.relationships.get(k, 0.0) + float(delta)

    def _get_rel(self, a: str, b: str) -> float:
        if a == b: return 0.0
        return self.relationships.get(self._rel_key(a, b), 0.0)

    def _decay_relationships(self, rate: float) -> None:
        if not self.relationships: return
        for k in list(self.relationships.keys()):
            self.relationships[k] *= (1.0 - rate)

    def _current_supporting_scores(self) -> List[tuple]:
        rows = []
        for cid in self.characters.keys():
            if cid == self.main_char_id: continue
            score = self._get_rel(self.main_char_id, cid)
            rows.append((cid, score))
        rows.sort(key=lambda r: r[1], reverse=True)
        return rows

    def _maybe_promote_or_demote(self) -> None:
        ranked = self._current_supporting_scores()
        self.supporting_ids = [cid for cid, _ in ranked[:3]]

    def _update_supporting_parentage(self, npc_ids: List[str]) -> None:
        if not self.supporting_ids: return
        for cid in npc_ids:
            if cid in self.supporting_ids or cid == self.main_char_id: continue
            best, best_s = None, -1e9
            for sid in self.supporting_ids:
                s = self._get_rel(cid, sid)
                if s > best_s: best, best_s = sid, s
            if best: self.characters[cid]["parent"] = best

    def _detect_characters(self, text: str) -> List[str]:
        tokens = text.split()
        return [t.strip(".,!?") for t in tokens if t.istitle() and t not in ("I", "You")]

    def _link_character(self, name: str) -> str:
        for cid, data in self.characters.items():
            if data.get("name") == name: return cid
        cid = f"C{len(self.characters)}"
        emb = self.encoder.encode(name)
        self.characters[cid] = {"name": name, "embedding": emb, "parent": None}
        return cid
    
def initialize_encoder():
    """
    Tries to initialize the Coral-accelerated encoder by looking for local files.
    If it fails, it falls back to a standard CPU-based encoder.
    All Coral-specific code is contained within the 'try' block.
    """
    try:
        from pycoral.utils.edgetpu import make_interpreter
        import sentencepiece as spm
        import os

        class CoralEncoder:
            MODEL_FILE = "model_edgetpu.tflite"
            TOKENIZER_FILE = "spm.model"

            def __init__(self):
                print("Attempting to load Coral-accelerated QA sentence encoder...")
                
                if not os.path.exists(self.MODEL_FILE) or not os.path.exists(self.TOKENIZER_FILE):
                    raise FileNotFoundError(
                        f"Could not find '{self.MODEL_FILE}' and '{self.TOKENIZER_FILE}'. "
                        "Please compile the model with Colab and place both files in your project directory."
                    )

                self.tokenizer = spm.SentencePieceProcessor()
                self.tokenizer.load(self.TOKENIZER_FILE) # type: ignore
                
                self.interpreter = make_interpreter(self.MODEL_FILE)
                self.interpreter.allocate_tensors()
                print("✅ CoralEncoder (QA Model) loaded successfully.")

            def encode(self, sentences: Union[str, List[str]]) -> np.ndarray:
                if isinstance(sentences, str):
                    return self._get_embedding(sentences)
                elif isinstance(sentences, list):
                    return np.array([self._get_embedding(s) for s in sentences])
                return np.array([])

            def _get_embedding(self, sentence: str) -> np.ndarray:
                input_ids = self.tokenizer.encode_as_ids([sentence]) # type: ignore
                
                self.interpreter.set_tensor(self.interpreter.get_input_details()[0]['index'], input_ids)
                self.interpreter.invoke()
                embedding = self.interpreter.get_tensor(self.interpreter.get_output_details()[0]['index'])[0]
                norm = np.linalg.norm(embedding)
                return embedding if norm == 0 else embedding / norm

        encoder = CoralEncoder()
        print("--- Encoder Initialized: Coral Edge TPU (Hardware Accelerated) ---")
        return encoder

    except Exception as e:
        print(f"\n--- WARNING: CoralEncoder failed to load ({e}). ---")
        print("--- Falling back to CPU-based SentenceTransformer. Performance will be slower. ---")
        encoder = SentenceTransformer('all-MiniLM-L6-v2')
        return encoder
    

class PhaseProcessor:
    """Processes a single macro temporal phase. Receives the encoder directly."""
    def __init__(self, encoder: Any, matrix: ModifierMatrix, user_input: str):
        self.encoder = encoder
        self.matrix = matrix
        self.user_input = user_input
        
    def process(self, phase_index: int, arc_data: Dict[str, dict]) -> Dict[str, dict]:
        processed_arcs = {}
        with ThreadPoolExecutor(max_workers=7) as executor:
            future_to_arc = {
                executor.submit(self._evaluate_single_arc, phase_index, arc_name, data): arc_name
                for arc_name, data in arc_data.items()
            }
            for future in future_to_arc:
                arc_name = future_to_arc[future]
                processed_arcs[arc_name] = future.result()
        return processed_arcs
            
    def _evaluate_single_arc(self, phase_index: int, arc_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Performs semantic scoring using the provided encoder."""
        scores = []
        triad_elements = []
        arc_text = data.get('text', "")
        
        for mod_index in range(3):
            element_text = self.matrix.get_element(phase_index, mod_index, RHETORICAL_ARCS.index(arc_name) + 1)
            try:
                embeddings = self.encoder.encode([arc_text, element_text])
                cosine_similarity = np.dot(embeddings[0], embeddings[1])
                scaled_score = cosine_similarity * 3.0
            except Exception as e:
                logging.warning(f"Scoring failed for arc '{arc_name}': {e}")
                scaled_score = 0.0

            scores.append(scaled_score)
            triad_elements.append(element_text)

        final_score = sum(scores) / len(scores) if scores else 0.0
        return {
            "text": arc_text,
            "magnitude": data.get('magnitude', 0),
            "triad_elements": triad_elements,
            "micro_scores": scores,
            "final_score": final_score,
            "triad_sign": _triad_sign(final_score)
        }

class LatticeMemoryStore:
    """Manages the file-based storage and retrieval of memory nodes."""
    def __init__(self):
        self.base_dir = LIBRARY_DIR
        os.makedirs(self.base_dir, exist_ok=True)
        
    def _get_node_path(self, coord_str: str) -> str:
        return os.path.join(self.base_dir, f"hypercube_{coord_str}.json")

    def read_node(self, coord_str: str) -> Dict:
        path = self._get_node_path(coord_str)
        if os.path.exists(path):
            with open(path, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {"entries": []}
        return {"entries": []}

    def write_entry(self, coord_str: str, entry_data: Dict):
        node_data = self.read_node(coord_str)
        node_data.setdefault("entries", []).append(entry_data)
        path = self._get_node_path(coord_str)
        with open(path, 'w') as f:
            json.dump(node_data, f, indent=2)
        logging.info(f"Memory entry saved to node: {coord_str}")

    def recall(self, coord_str: str, num_entries: int = 5) -> List[Dict]:
        node_data = self.read_node(coord_str)
        return node_data.get("entries", [])[-num_entries:]

    def list_nodes_meta(self) -> List[Dict]:
        nodes_meta = []
        for filename in os.listdir(self.base_dir):
            if filename.startswith("hypercube_") and filename.endswith(".json"):
                coord_str = filename.replace("hypercube_", "").replace(".json", "")
                nodes_meta.append({"coordinate": coord_str, "file": filename})
        return nodes_meta