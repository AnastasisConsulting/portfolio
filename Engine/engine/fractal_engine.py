"""
Copyright (c) 2025 William Wallace
G-Synthetic Project

Usage of this code is subject to the MIT license + G-Synthetic Addendum + Patent Notice.
See LICENSE file for full terms.
"""

import json
import os
import datetime
import logging
import numpy as np
from typing import Dict, Any, List, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from llm_tank.llm_core import LLMManager

# Base CPU class, used for the fallback and by the CoralEncoder for tokenization
from sentence_transformers import SentenceTransformer

# --- LATTICE CONSTANTS (DETERMINISTIC GEOMETRY) ---
# Axis assignment: x=Characters, y=GeoMemory (World), z=Story  (increasing vertically)
TRANSFORMS = ["Characters", "GeoMemory", "Story"]
TRANSFORM_INDEX = {name: i for i, name in enumerate(TRANSFORMS)}

MODIFIERS = {
    "Characters": ["MainCharacter", "CoStars", "NPCs"],
    "GeoMemory":  ["WorldState", "Factions", "ForcesAtPlay"],
    "Story":      ["Setup", "Confrontation", "Resolution"],
}
MOD_INDEX = {t: {m: i for i, m in enumerate(mods)} for t, mods in MODIFIERS.items()}

# The 7 rhetorical arcs (fixed order → deterministic tic indices)
ARCS = ["Essence", "Form", "Function", "Context", "Intent", "Relation", "Value"]
ARC_INDEX = {name: i for i, name in enumerate(ARCS)}

def encode_coord_idx(t_idx: int, m_idx: int, e_idx: int) -> int:
    """Unique integer ID in [0, 62] for any (transform, modifier, tic)."""
    return (t_idx * 21) + (m_idx * 7) + e_idx

def decode_coord_idx(coord_id: int) -> tuple[int, int, int]:
    """Inverse of encode_coord_idx."""
    t_idx = coord_id // 21
    rem = coord_id % 21
    m_idx = rem // 7
    e_idx = rem % 7
    return t_idx, m_idx, e_idx

def encode_coord_str(t_idx: int, m_idx: int, e_idx: int) -> str:
    """Compact, file-safe coordinate string."""
    return f"x{t_idx}-y{m_idx}-z{e_idx}"

def decode_coord_str(s: str) -> tuple[int, int, int]:
    parts = s.split("-")
    return int(parts[0][1:]), int(parts[1][1:]), int(parts[2][1:])


# --- 1. MEMORY & FILE SYSTEM MANAGEMENT ---
MEMORY_DIR = "game_data/memory"
SCAFFOLDING_FILE = os.path.join(MEMORY_DIR, "narrative_scaffolding.json")
LIBRARY_DIR = os.path.join(MEMORY_DIR, "hypercube_library")

def _pad7(lst: List[str]) -> List[str]:
    # Ensures exactly 7 tics per modifier (placeholders are empty strings).
    return (lst + [""] * 7)[:7]

def initialize_filesystem():
    """Initializes the directory structure and the 'blank slate' memory files."""
    os.makedirs(LIBRARY_DIR, exist_ok=True)
    os.makedirs(MEMORY_DIR, exist_ok=True)

    if not os.path.exists(SCAFFOLDING_FILE):
        print(f"INITIALIZING: Creating new narrative scaffolding at '{SCAFFOLDING_FILE}'...")
        scaffolding = {
            "meta": {"current_chapter": 1},
            "transforms": {
                "GeoMemory": {
                    "WorldState":     _pad7(["A dimly lit tavern", "The world outside", "A forgotten ruin"]),
                    "Factions":       _pad7(["The concept of 'self'", "The tavern's unspoken rules"]),
                    "ForcesAtPlay":   _pad7(["The bar", "A shadowy corner", "The front door"]),
                },
                "Characters": {
                    "MainCharacter":  _pad7(["Protagonist identity", "Role, archetype", "Personal goals"]),
                    "CoStars":        _pad7(["Key supporting characters", "Their roles", "How they enable/impede"]),
                    "NPCs":           _pad7(["Ambient personalities", "Types, professions", "Services, obstacles"]),
                },
                "Story": {
                    "Setup":          _pad7(["The premise and initial condition", "Exposition structure", "What kicks the motion"]),
                    "Confrontation":  _pad7(["The central struggle crystallized", "Escalation pattern", "Trials, schemes, and counters"]),
                    "Resolution":     _pad7(["The decisive break and new equilibrium", "Climax mechanics", "Final actions and consequences"]),
                }
            }
        }
        with open(SCAFFOLDING_FILE, 'w') as f:
            json.dump(scaffolding, f, indent=2)

    initial_chapter_file = os.path.join(LIBRARY_DIR, "hypercube_chapter_01.json")
    if not os.path.exists(initial_chapter_file):
        print(f"INITIALIZING: Creating Chapter 1 at '{initial_chapter_file}'...")
        chapter_zero = {
            "meta": {
                "chapter": 1,
                "summary": "The beginning of the journey.",
                "timestamp_start": datetime.datetime.utcnow().isoformat()
            },
            "axis_definitions": {
                "x_axis": {"theme": "Characters", "modifiers": MODIFIERS["Characters"]},
                "y_axis": {"theme": "GeoMemory", "modifiers": MODIFIERS["GeoMemory"]},
                "z_axis": {"theme": "Story",     "modifiers": MODIFIERS["Story"]},
            },
            "nodes": {}  # lattice entries will accrue over time
        }
        with open(initial_chapter_file, 'w') as f:
            json.dump(chapter_zero, f, indent=2)


DECOMPOSITION_PROMPT = """
You are a master of symbolic decomposition. Your task is to analyze the following input and deconstruct it into 7 universal logical chunks based on the provided definitions. Your output must be a single, valid JSON object where each key is one of the 7 arcs and the value is the extracted content as a string.

# Definitions
- Essence: Core identity, nature, or type. What the input
"""

SYNTHESIS_PROMPT = """
You are a master storyteller and game master for the game Eideus Dawn. Your task is to provide a response in a valid JSON format with five specific keys. Do not add any text before or after the JSON object.

# Example Input
Player's Action: "I look at the bartender."
Memory Coordinate: "x0-y2-z0"

# Example Output
{{
  "narrative": "You turn your attention to the bartender, a burly man with a weary expression. He pauses his work, wiping a mug with a stained rag, and meets your gaze with a hint of curiosity.",
  "character_aspect": "This action marks your first conscious decision to engage with another person.",
  "world_aspect": "The bartender is established as a key figure in this immediate environment.",
  "story_aspect": "An opportunity for dialogue and information gathering has been created.",
  "ascii_map": "#########################\n#        B              #\n#       ---             #\n#      |   |            #\n#                       #\n#   @                   #\n#                       #\n#                       #\n#                       #\n#                       #\n#                       #\n#########################"
}}

# Current Task
Player's Action: "{player_input}"
Memory Coordinate: "{coordinate_string}"

# Output
"""

CHAPTER_INDEX_FILE = os.path.join(LIBRARY_DIR, "hypercube_index.json")

def _load_chapter_index() -> Dict[str, Any]:
    """Load or initialize the unified chapter index file."""
    if not os.path.exists(CHAPTER_INDEX_FILE):
        index = {"chapters": {}}
        with open(CHAPTER_INDEX_FILE, "w") as f:
            json.dump(index, f, indent=2)
        return index
    with open(CHAPTER_INDEX_FILE, "r") as f:
        return json.load(f)

def _save_chapter_index(index: Dict[str, Any]):
    """Save the unified chapter index back to disk."""
    with open(CHAPTER_INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)

# --- DETERMINISTIC ROUTERS (keyword heuristics; no probabilities) ---

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
    return ARC_INDEX.get(dominant_arc, 0)


def initialize_encoder():
    """
    Tries to initialize the Coral-accelerated encoder.
    All Coral-specific imports and code are contained locally within the 'try' block.
    If it fails, it falls back to the standard CPU-based encoder.
    """
    try:
        # --- Conditional Imports and Class Definition ---
        from pycoral.utils.edgetpu import make_interpreter
        import urllib.request

        class CoralEncoder:
            MODEL_URL = "https://coral.ai/static/models/edgetpu/all-MiniLM-L6-v2_quant_edgetpu.tflite"
            MODEL_FILE = "all-MiniLM-L6-v2_quant_edgetpu.tflite"
            TOKENIZER_NAME = 'sentence-transformers/all-MiniLM-L6-v2'

            def __init__(self):
                self._download_model()
                self.tokenizer = SentenceTransformer(self.TOKENIZER_NAME).tokenizer
                self.interpreter = make_interpreter(self.MODEL_FILE)
                self.interpreter.allocate_tensors()

            def _download_model(self):
                if not os.path.exists(self.MODEL_FILE):
                    print(f"Downloading model: {self.MODEL_FILE}...")
                    urllib.request.urlretrieve(self.MODEL_URL, self.MODEL_FILE)

            def encode(self, sentence: Union[str, List[str]]) -> np.ndarray:
                if isinstance(sentence, str):
                    return self._get_embedding(sentence)
                elif isinstance(sentence, list):
                    return np.array([self._get_embedding(s) for s in sentence])
                return np.array([]) # Return empty array for unexpected types

            def _get_embedding(self, sentence: str) -> np.ndarray:
                inputs = self.tokenizer.encode(sentence, return_tensors='np')
                input_ids = inputs.astype(np.int32)
                self.interpreter.set_tensor(self.interpreter.get_input_details()[0]['index'], input_ids)
                self.interpreter.invoke()
                embedding = self.interpreter.get_tensor(self.interpreter.get_output_details()[0]['index'])[0]
                norm = np.linalg.norm(embedding)
                if norm == 0:
                   return embedding
                return embedding / norm

        # --- Attempt to create the hardware-accelerated encoder ---
        encoder = CoralEncoder()
        print("--- Encoder Initialized: Coral Edge TPU (Hardware Accelerated) ---")
        return encoder

    except Exception as e:
        # --- Fallback to CPU version ---
        print(f"\n--- WARNING: CoralEncoder failed to load ({e}). ---")
        print("--- Falling back to CPU-based SentenceTransformer. Performance will be slower. ---")
        encoder = SentenceTransformer('all-MiniLM-L6-v2')
        return encoder


# --- 3. THE FRACTAL MEMORY ENGINE ---

class FractalMemoryEngine:
    def __init__(self, llm_manager: "LLMManager"):
        """
        Core memory engine for narrative scaffolding and character/world/story state.
        """
        self.llm_manager = llm_manager
        self.store = LatticeMemoryStore()
        self.encoder = initialize_encoder()
        self.turn_cache: List[Dict[str, Any]] = []
        self.vector_index = None
        self.current_chapter_num: int = 1
        self.main_char_id: str = "MC"
        self.characters: Dict[str, Dict[str, Any]] = {
            self.main_char_id: {"name": "Player", "embedding": None, "parent": None}
        }
        self.supporting_ids: List[str] = []
        self.relationships: Dict[tuple, float] = {}
        self.world_modifiers = {
            "novelty": [],
            "geopolitics": [],
            "landmarks": {}
        }
        self.story_roles = {
            "protagonists": set(),
            "antagonists": set(),
            "sentiment": {}
        }
        self.mutation_cooldown: int = 0

    def _call_llm_agent(self, agent_prompt: str, **kwargs) -> str:
        active_llm = self.llm_manager.get_active_llm()
        if not active_llm or not active_llm.is_loaded:
            print("\n--- LLM AGENT FAILED: No active LLM loaded in the manager. ---")
            return json.dumps({"narrative": "Error: LLM not available."})
        
        final_prompt = agent_prompt.format(**kwargs)
        
        print("\n" + "="*50)
        print(f"--- Calling LLM Agent: {active_llm.get_name()} ---")
        print(f"--- PROMPT START ---")
        print(final_prompt)
        print(f"--- PROMPT END ---")
        
        try:
            response_text = active_llm.generate_response(prompt=final_prompt, history=[], hyperparameters={})
            print(f"--- RAW LLM RESPONSE ---")
            print(response_text)
            print("="*50 + "\n")
        except Exception as e:
            print(f"--- LLM GENERATION FAILED: {e} ---")
            return json.dumps({"narrative": f"Error during LLM call: {e}"})

        response_text = response_text.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].strip()
        if "```" in response_text:
            response_text = response_text.split("```")[0].strip()
        return response_text
        
    def run_turn(self, player_input: str) -> Dict:
        print(f"\n>>> PLAYER INPUT: \"{player_input}\"")

        # 1) Decompose → arcs
        decomposed_arcs_str = self._call_llm_agent(DECOMPOSITION_PROMPT, player_input=player_input)
        try:
            decomposed_arcs_dict = json.loads(decomposed_arcs_str)
        except json.JSONDecodeError as e:
            print(f"\n--- JSON PARSING ERROR: {e} ---")
            print(f"Mal-formatted LLM output: {decomposed_arcs_str}")
            return {"error": "Failed to parse LLM output."}

        # 2) Token counts
        arc_token_counts = {arc: len((decomposed_arcs_dict.get(arc, "") or "").split()) for arc in ARCS}
        dominant_arc = max(arc_token_counts.items(), key=lambda kv: kv[1])[0]

        # 3) Character detection & relationship maintenance
        mentioned_texts = self._detect_characters(player_input)
        mentioned_ids: List[str] = [self._link_character(m) for m in mentioned_texts]
        self._score_interaction(self.main_char_id, mentioned_ids, player_input)
        self._update_supporting_parentage(mentioned_ids)
        self._maybe_promote_or_demote()

        # 4) Rank arcs for telemetry
        ranked_arcs = sorted(arc_token_counts.items(), key=lambda item: item[1], reverse=True)
        arc_ranking = {arc: rank for rank, (arc, _) in enumerate(ranked_arcs)}
        ranked_arcs_dict = {arc: arc_ranking[arc] for arc in ARCS}

        # 5) Deterministic coordinate routing
        t_idx = route_transform(player_input)
        m_idx = route_modifier(t_idx, player_input, mentioned_texts)
        e_idx = route_tic(dominant_arc)
        coord_str = encode_coord_str(t_idx, m_idx, e_idx)
        coord_id = encode_coord_idx(t_idx, m_idx, e_idx)

        # 6) Synthesis with the resolved coordinate
        response_json_str = self._call_llm_agent(
            SYNTHESIS_PROMPT,
            player_input=player_input,
            coordinate_string=coord_str
        )

        try:
            synthesized_data = json.loads(response_json_str)
        except json.JSONDecodeError:
            synthesized_data = {"narrative": "The world feels hazy and indistinct...", "error": "synthesis_parse_fail"}

        # 7) Build event and write-through to lattice node
        event = {
            "coord": coord_str,
            "coord_id": coord_id,
            "transform": TRANSFORMS[t_idx],
            "modifier": MODIFIERS[TRANSFORMS[t_idx]][m_idx],
            "tic_arc": dominant_arc,
            "type": "turn",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "player_input": player_input,
            "arcs": decomposed_arcs_dict,
            "ranked_arcs": ranked_arcs_dict,
            "synthesis": synthesized_data
        }
        self.turn_cache.append(event)
        self.store.write_entry(coord_str, event)
        print(f"Filed at {coord_str} ({TRANSFORMS[t_idx]} / {MODIFIERS[TRANSFORMS[t_idx]][m_idx]} / {dominant_arc})")
        
        final_output = {
            "coordinate": coord_str,
            "ranked_arcs": ranked_arcs_dict,
        }
        final_output.update(synthesized_data)
        return final_output

    def trigger_mutation(self) -> Dict:
        """Generates a spontaneous, surprising event."""
        print(">>> TRIGGERING STORY MUTATION...")
        mutation_prompt = "A surprising, unexpected event occurs in the tavern."
        coord_str = "mutation-event"

        response_json_str = self._call_llm_agent(
            SYNTHESIS_PROMPT,
            player_input=mutation_prompt,
            coordinate_string=coord_str
        )
        try:
            synthesized_data = json.loads(response_json_str)
        except json.JSONDecodeError:
            synthesized_data = {"narrative": "A sudden silence falls over the tavern.", "error": "mutation_parse_fail"}

        return synthesized_data

    def recall_similar_events(self, query: str, top_k: int = 5) -> List[Dict]:
        """Recall most similar past events using semantic embeddings."""
        if self.vector_index is None:
            print("No vector index initialized.")
            return []
        query_embedding = self.encoder.encode(query)
        # Placeholder for actual vector search
        # results = self.vector_index.search(query_embedding, top_k)
        # return [self._fetch_event_by_id(r.id) for r in results]
        return []

    def _fetch_event_by_id(self, event_id: str) -> Dict[str, Any]:
        """Stub: retrieve an event by ID from persistent storage."""
        return {"id": event_id, "stub": True}

    def flush_cache_to_file(self):
        """Write cached events to the chapter’s persistent JSON timeline."""
        if not self.turn_cache:
            return
        index = _load_chapter_index()
        chapter_key = f"chapter_{self.current_chapter_num:02d}"
        if chapter_key not in index["chapters"]:
            index["chapters"][chapter_key] = {"timeline": []}
        index["chapters"][chapter_key]["timeline"].extend(self.turn_cache)
        _save_chapter_index(index)
        print(f"Flushed {len(self.turn_cache)} events to {chapter_key}.")
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
    
    def archive_modifier_snapshot(self, t_idx: int, m_idx: int, reason: str = "") -> str:
        ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        archive_dir = os.path.join(LIBRARY_DIR, "archive")
        os.makedirs(archive_dir, exist_ok=True)
        meta = {
            "timestamp": ts,
            "reason": reason,
            "transform": TRANSFORMS[t_idx],
            "modifier": MODIFIERS[TRANSFORMS[t_idx]][m_idx],
            "coords": [encode_coord_str(t_idx, m_idx, e) for e in range(7)]
        }
        entries = []
        for e in range(7):
            coord = encode_coord_str(t_idx, m_idx, e)
            last = self.store.recall(coord, num_entries=1)
            entries.append({"coord": coord, "last_entry": last[0] if last else None})
        payload = {"meta": meta, "entries": entries}
        path = os.path.join(archive_dir, f"archive_{TRANSFORMS[t_idx]}_{m_idx}_{ts}.json")
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        return path


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
                return json.load(f)
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