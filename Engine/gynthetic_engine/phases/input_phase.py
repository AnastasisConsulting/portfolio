# Auto-generated placeholder
from typing import List, Dict

class InputPhaseProcessor:
    def __init__(self, modifier_matrix):
        self.matrix = modifier_matrix

    def build_input_triads(self, arc_ranks: Dict[str, int]) -> Dict[str, List[str]]:
        """
        Build triads for the Input Phase (Phase 0).
        Pulls 1 element per modifier per arc, based on rank.
        Returns dict of arc → triad list (length 3).
        """
        phase_index = 0  # Input Phase
        arc_triads = {}

        for arc, rank in arc_ranks.items():
            triad = []
            for mod_index in range(3):
                try:
                    value = self.matrix.get_element(phase_index, mod_index, rank)
                    triad.append(value if value else "[Missing Element]")
                except Exception as e:
                    print(f"⚠️ Failed to get element for arc '{arc}', mod {mod_index}, rank {rank}: {e}")
                    triad.append("[Missing Element]")
            arc_triads[arc.lower()] = triad

        return arc_triads
