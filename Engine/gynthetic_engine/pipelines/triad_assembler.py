# Auto-generated placeholder
from typing import Dict, List

ARC_ORDER = [
    "essence", "form", "action", "frame", "intent", "relation", "value"
]

def assemble_triads(
    transform_data: Dict,
    arc_ranks: Dict[str, int]
) -> Dict[str, List[List[str]]]:
    """
    For each arc, select one element (by rank index) per modifier per transform phase.
    Returns: Dict mapping arc name → list of 3 triads (each triad = list of 3 elements)
    """
    arc_triads = {}

    for arc_name in ARC_ORDER:
        rank = arc_ranks.get(arc_name, 0)  # index 0–6
        triads = []
        for transform in transform_data.get("transforms", []):
            phase_triads = []
            for modifier in transform.get("modifiers", []):
                elements = modifier.get("elements", [])
                if rank < len(elements):
                    phase_triads.append(elements[rank])
                else:
                    phase_triads.append("[Missing Element]")
            triads.append(phase_triads)

        arc_triads[arc_name] = triads

    return arc_triads
