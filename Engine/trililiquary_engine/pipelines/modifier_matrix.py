# Auto-generated placeholder
from typing import List, Dict

class ModifierMatrix:
    def __init__(self, transform_data: Dict):
        self.grid = self._build_matrix(transform_data)

    def _build_matrix(self, data: Dict) -> List[List[List[str]]]:
        """
        Builds a 3x3 grid (phases × modifiers) of elements.
        Returns a matrix of shape [3][3][7] = [phases][modifiers][elements]
        """
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
            index = rank_index - 1  # 1-based to 0-based
            if 0 <= index < len(elements):
                value = elements[index]
                print(f"✅ get_element → phase:{phase_index}, mod:{mod_index}, rank:{rank_index} → {value}")
                return value
            else:
                print(f"❌ Rank {rank_index} out of bounds for phase:{phase_index}, mod:{mod_index}.")
                return "[Missing Element]"
        except Exception as e:
            print(f"❌ get_element({phase_index}, {mod_index}, {rank_index}) failed: {e}")
            return "[Missing Element]"
