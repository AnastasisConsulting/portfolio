"""
Copyright (c) 2025 William Wallace
G-Synthetic Project

Usage of this code is subject to the MIT license + G-Synthetic Addendum + Patent Notice.
See LICENSE file for full terms.
"""


import json
import re
import os
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

# --- Local Eideus Dawn Project Imports ---
from llm_tank.adapters.ollama_adapter import LLMClient as OllamaLLMClient
from PySide6.QtCore import QObject

# --- ADDED: CORE DATA STRUCTURES & CONSTANTS ---
RHETORICAL_ARCS = ("essence", "form", "action", "frame", "intent", "relation", "value")
MACRO_PHASES = ("Input", "Identity", "Inception")

# --- ADDED: LLM INTERFACE (Required by the engine) ---
class LLMInterface:
    def __init__(self, provider: str, config: Dict = {}):
        self.provider = provider
        self.adapter = None
        if provider == "Ollama":
            self.adapter = OllamaLLMClient(
                base_url=config.get("base_url", "http://127.0.0.1:11434"),
                model=config.get("model", "llama2-uncensored:latest")
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    # Placeholder for actual LLM calls
    def decompose_input(self, user_input: str) -> Dict[str, dict]: return {arc: {"text": "mock", "magnitude": 1} for arc in RHETORICAL_ARCS}
    def score_relevance(self, arc_text: str, user_input: str, template_text: str) -> float: return 0.5
    def synthesize_output(self, prompt_stack: List[Dict[str, Any]]) -> str: return "This is the final synthesized response."

# --- ADDED: TEMPLATE & MODIFIER HIERARCHY ---
class TemplateLoader:
    def __init__(self, character: str, base_dir: str = "main_app/engine/templates"):
        self.filepath = Path(base_dir) / "geo_char_story_template.json"
    def load(self) -> Dict:
        with self.filepath.open("r") as f: return json.load(f)

class ModifierMatrix:
    def __init__(self, template_data: Dict):
        self.grid: List[List[List[str]]] = self._build_matrix(template_data)
    def _build_matrix(self, data: Dict) -> List[List[List[str]]]:
        matrix = []
        for transform in data.get("transforms", []):
            row = []
            for modifier in transform.get("modifiers", []):
                row.append(modifier.get("elements", []))
            matrix.append(row)
        return matrix
    def get_element(self, phase_index: int, mod_index: int, rank_index: int) -> str:
        try:
            elements = self.grid[phase_index][mod_index]
            index = rank_index - 1
            return elements[index] if 0 <= index < len(elements) else ""
        except IndexError: return ""

# --- ADDED: PHASE PROCESSOR ---
class PhaseProcessor:
    def __init__(self, llm_interface: LLMInterface, matrix: ModifierMatrix, user_input: str):
        self.llm_interface = llm_interface
        self.matrix = matrix
        self.user_input = user_input
    def process(self, phase_index: int, arc_data: Dict[str, dict]) -> Dict[str, dict]:
        # This is a simplified process for a single pass
        return {arc: self._evaluate_single_arc(phase_index, arc, data) for arc, data in arc_data.items()}
    def _evaluate_single_arc(self, phase_index: int, arc_name: str, data: Dict) -> Dict[str, Any]:
        scores, triad_elements = [], []
        for mod_index in range(3):
            element = self.matrix.get_element(phase_index, mod_index, RHETORICAL_ARCS.index(arc_name) + 1)
            scores.append(self.llm_interface.score_relevance(data['text'], self.user_input, element))
            triad_elements.append(element)
        return {"text": data.get('text', ""), "magnitude": data.get('magnitude', 0), "triad_elements": triad_elements, "final_score": sum(scores) / 3 if scores else 0.0}

# --- THE MAIN ENGINE ORCHESTRATOR ---
class SymbolicEngine(QObject):
    """
    The main class that orchestrates the cognitive pipeline.
    """
    def __init__(self, llm_manager: Any, character: str = "default"):
        super().__init__()
        # FIX: Store llm_manager and character as instance attributes
        self.llm_manager = llm_manager
        self.character = character

    def run_pipeline(self, user_input: str) -> str:
        """
        Executes a single transform pass (1/3 of the full engine).
        """
        print("🌀 Starting 1/3 Engine Pass...")
        
        # FIX: Access llm_manager from self
        llm_provider = self.llm_manager.get_name()
        llm_config = self.llm_manager.config
        llm_interface = LLMInterface(llm_provider, llm_config)
        
        print("  1. Decomposing input...")
        arc_data = llm_interface.decompose_input(user_input)
        
        template = TemplateLoader(self.character).load()
        modifier_matrix = ModifierMatrix(template)
        
        print("  2. Processing arcs through Input Phase...")
        phase_processor = PhaseProcessor(llm_interface, modifier_matrix, user_input)
        phase_results = phase_processor.process(0, arc_data)
            
        print("  3. Assembling final prompt...")
        final_prompt_stack = []
        for arc_name in RHETORICAL_ARCS:
            arc_result = phase_results[arc_name]
            
            compiled_triads_str = " ".join(arc_result['triad_elements'])
            final_scores_str = f"Input:{arc_result['final_score']:.2f}"
            text = arc_result['text']
            magnitude = arc_result['magnitude']
            
            final_prompt_stack.append({
                "arc": arc_name,
                "rank": RHETORICAL_ARCS.index(arc_name) + 1,
                "scores": final_scores_str,
                "magnitude": magnitude,
                "compiled_prompt": f"Text: {text}\nTriads: {compiled_triads_str}"
            })
            
        print("  4. Submitting to Synthesis LLM...")
        final_response = llm_interface.synthesize_output(final_prompt_stack)
        return final_response