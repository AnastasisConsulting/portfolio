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
from dataclasses import dataclass
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

def _triad_sign(x: float) -> int:
    """Maps a score from [-3, 3] to -1, 0, or 1."""
    if x > 0.15: return 1
    if x < -0.15: return -1
    return 0

# --- LATTICE CONSTANTS ---
RHETORICAL_ARCS = ("essence", "form", "action", "frame", "intent", "relation", "value")
MACRO_PHASES = ("Input", "Identity", "Inception")

# --- DATA CLASSES & HELPERS ---
@dataclass
class RhetoricalArcs:
    essence: str = ""
    form: str = ""
    action: str = ""
    frame: str = ""
    intent: str = ""
    relation: str = ""
    value: str = ""# --- 1. MEMORY & FILE SYSTEM MANAGEMENT ---
MEMORY_DIR = "game_data/memory"
SCAFFOLDING_FILE = os.path.join(MEMORY_DIR, "narrative_scaffolding.json")
LIBRARY_DIR = os.path.join(MEMORY_DIR, "hypercube_library")

# ... (initialize_filesystem function and other file helpers would go here) ...

# --- 2. THE FOUR LLM AGENT PROMPTS ---
DECOMPOSITION_PROMPT = """
You are a master of symbolic decomposition. Your task is to analyze the following input and deconstruct it into 7 universal logical chunks based on the provided definitions. Your output must be a single, valid JSON object where each key is one of the 7 arcs and the value is the extracted content as a string.

# Definitions
- Essence: Core identity, nature, or type. What the input inherently is.
- Form: Shape, configuration, format, or syntax. The observable structure.
- Function: Its role, behavior, or operative output. What it does.
- Context: The spatial, temporal, or situational frame.
- Intent: The purpose or drive behind the input.
- Relation: Interfacing or interacting elements; its connections.
- Value: Its qualitative or quantitative significance or impact.

Input: "{player_input}"
Output:
"""

SYNTHESIS_PROMPT = """
You are a master storyteller and game master for the game Eideus Dawn. A player, who is an amnesiac in a tavern, has taken an action. Based on the provided ranked and scored data, provide a response in a valid JSON format with five specific keys:
1. "narrative": A compelling, second-person narrative response (2-3 sentences).
2. "character_aspect": A single sentence on the event's character significance.
3. "world_aspect": A single sentence on the event's world-building significance.
4. "story_aspect": A single sentence on how the event pushes the story forward.
5. "ascii_map": A simple, top-down ASCII art map of the immediate area (25 characters wide, 12 lines high). Use '@' for the player, capital letters for important NPCs (e.g., 'B' for Bartender), '#' for walls, and simple symbols for furniture.

# Ranked & Scored Data
{formatted_input}

# Output
"""

class TemplateLoader:
    """Loads plug-and-play domain templates."""
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
    """Manages the 3x3 grid of elements from a loaded template."""
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

            def encode(self, sentences: Union[str, List[str]]) -> np.ndarray:
                if isinstance(sentences, str):
                    return self._get_embedding(sentences)
                elif isinstance(sentences, list):
                    return np.array([self._get_embedding(s) for s in sentences])
                return np.array([])

            def _get_embedding(self, sentence: str) -> np.ndarray:
                inputs = self.tokenizer.encode(sentence, return_tensors='np')
                input_ids = inputs.astype(np.int32)
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
        return SentenceTransformer('all-MiniLM-L6-v2')

class PhaseProcessor:
    """Processes a single macro temporal phase. Now receives the encoder directly."""
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
    

class SymbolicEngine(QObject):
    """
    The main orchestrator, now directly handling all LLM and encoder interactions.
    """
    def __init__(self, llm_manager: LLMManager, character: str = "default"):
        super().__init__()
        self.llm_manager = llm_manager
        self.character = character
        self.memory_store = LatticeMemoryStore()
        self.encoder = initialize_encoder()
        # ... (other state initializations from your original file) ...
        self.turn_cache = []
        self.vector_index = None
        self.current_chapter_num = 1
        self.main_char_id = "MC"
        self.characters = {self.main_char_id: {"name": "Player", "embedding": None, "parent": None}}
        self.supporting_ids = []
        self.relationships = {}

    def _call_llm_agent(self, agent_prompt: str, **kwargs) -> str:
        active_llm = self.llm_manager.get_active_llm()
        if not active_llm or not active_llm.is_loaded:
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

    def run_pipeline(self, user_input: str, coord_prefix: tuple = (0,0,0)) -> Dict[str, Any]:
        """Main processing pipeline for a user turn."""
        # ... This is the large method from the previous response ...
        # It handles the full 5-step process: Decompose, Process, Retrieve, Rank, Synthesize
        # and returns the final dictionary for the UI.
        # (Pasting the full method here for completeness)
        print("🌀 Starting Engine Orchestration...")
        coord = next_page_for(coord_prefix)
        save_x_up(coord, user_input)

        arc_data_str = self._call_llm_agent(DECOMPOSITION_PROMPT, player_input=user_input)
        try:
            arc_data = json.loads(arc_data_str)
        except json.JSONDecodeError:
            return {"narrative": "Error: Failed to understand the structure of the action."}

        template = TemplateLoader(self.character).load()
        modifier_matrix = ModifierMatrix(template)

        all_phase_results: dict[str, dict] = {}
        for phase_index, phase_name in enumerate(MACRO_PHASES):
            processor = PhaseProcessor(self.encoder, modifier_matrix, user_input)
            results = processor.process(phase_index, arc_data)
            all_phase_results[phase_name] = results
        
        # This is a placeholder for your full ranking and memory retrieval logic
        formatted_input = "Data has been processed and ranked..."

        final_response_str = self._call_llm_agent(SYNTHESIS_PROMPT, formatted_input=formatted_input)
        
        try:
            final_response_dict = json.loads(final_response_str)
        except json.JSONDecodeError:
            final_response_dict = {"narrative": final_response_str or "The world remains silent."}
        
        return final_response_dict

    def trigger_mutation(self) -> Dict[str, Any]:
        """Generates a spontaneous, surprising event."""
        print(">>> TRIGGERING STORY MUTATION...")
        mutation_prompt = "A surprising, unexpected event occurs in the tavern."
        # You might want a different coordinate system for mutations
        coord_str = "mutation-event"
        
        response_json_str = self._call_llm_agent(
            SYNTHESIS_PROMPT,
            # Using a simplified placeholder for the formatted input
            formatted_input=f"[MUTATION]\n{mutation_prompt}"
        )
        try:
            return json.loads(response_json_str)
        except json.JSONDecodeError:
            return {"narrative": "A sudden silence falls over the tavern."}

    # ... (All other helper methods for SymbolicEngine like _score_interaction, _link_character, etc., go here) ...

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