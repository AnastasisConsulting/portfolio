# triadic_output_builder.py

from typing import Dict, List

ARC_ORDER = [
    "Essence", "Form", "Action", "Frame", "Intent", "Relation", "Value"
]

def build_prompt_stack(
    triads_by_arc: Dict[str, List[List[str]]],
    ranked_pipeline_ids: List[str]
) -> List[Dict[str, str]]:
    """
    Assemble final prompt stack ordered by pipeline ranking.
    Each entry contains: pipeline_id, arc, and joined prompt string.
    """
    arc_to_pipeline = dict(zip(ARC_ORDER, [f"pipeline_{i+1}" for i in range(7)]))
    pipeline_to_arc = {v: k for k, v in arc_to_pipeline.items()}

    stack = []
    for pipeline_id in ranked_pipeline_ids:
        arc = pipeline_to_arc.get(pipeline_id)
        if not arc:
            continue

        triads = triads_by_arc.get(arc, [])
        compiled = "\n".join([" ".join(triad) for triad in triads])

        stack.append({
            "pipeline_id": pipeline_id,
            "arc": arc,
            "compiled_prompt": compiled
        })

    return stack

def build_ranked_output_payload(rank_system, processed_pipelines):
    """
    Builds a vertical 1-column table (1–7) of triadic pipeline data for the Composer.

    Parameters:
    - rank_system: system object with get_priority_map() → Dict[arc_label, rank_number]
    - processed_pipelines: Dict[str, Any], keyed by arc_label with triadic results

    Returns:
    - dict in the form { "ranked_output": { "1": {...}, ..., "7": {...} } }
    """
    priority_map = rank_system.get_priority_map()  # e.g., {"Essence": 3, ...}
    ranked_output = {str(i): None for i in range(1, 8)}

    for arc, rank in priority_map.items():
        triad_data = processed_pipelines.get(arc, {})
        ranked_output[str(rank)] = triad_data

    return { "ranked_output": ranked_output }
