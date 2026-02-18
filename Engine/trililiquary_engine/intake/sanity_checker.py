# sanity_checker.py

from typing import Dict, List
from .arc_struct import ARC_ORDER


def check_arc_balance(triads: Dict[str, List[List[str]]]) -> Dict[str, str]:
    """
    Evaluate the epistemic integrity of each arc.
    Returns a dictionary mapping arc names to health flags:
        - "green" = healthy
        - "yellow" = underdeveloped or sparse
        - "red" = missing or dangerously unbalanced
    """
    arc_flags = {}

    for arc in ARC_ORDER:
        triad_set = triads.get(arc, [])
        empty_count = 0

        for triad in triad_set:
            if all(el == "[Missing Element]" or not el.strip() for el in triad):
                empty_count += 1

        if empty_count == 0:
            arc_flags[arc] = "green"
        elif empty_count <= 1:
            arc_flags[arc] = "yellow"
        else:
            arc_flags[arc] = "red"

    return arc_flags


def evaluate_overall_sanity(arc_flags: Dict[str, str]) -> str:
    """
    Determines overall system health:
        - "green" = all arcs healthy
        - "yellow" = minor imbalance
        - "red" = at least one arc critically malformed
    """
    if all(flag == "green" for flag in arc_flags.values()):
        return "green"
    elif "red" in arc_flags.values():
        return "red"
    else:
        return "yellow"


def summarize_issues(arc_flags: Dict[str, str]) -> List[str]:
    """
    Returns human-readable labels of flagged arcs (non-green).
    Useful for UI diagnostics and trace logs.
    """
    return [f"{arc.title()}: {status}" for arc, status in arc_flags.items() if status != "green"]


# Optional dry-run test logic
if __name__ == "__main__":
    sample_triads = {
        "essence": [["truth", "being", "fact"], ["truth", "", "fact"], ["", "", ""]],
        "form": [["structure", "shape", "logic"], ["form", "logic", "structure"], ["form", "logic", ""]],
        "action": [["create", "", ""], ["", "", ""], ["do", "", ""]],
        "frame": [["context", "scope", "limit"], ["", "", ""], ["frame", "scope", "limit"]],
        "intent": [["will", "purpose", "goal"], ["", "", ""], ["intention", "", ""]],
        "relation": [["bond", "link", "association"], ["", "", ""], ["", "", ""]],
        "value": [["good", "meaning", ""], ["worth", "virtue", "ideal"], ["", "", ""]],
    }

    flags = check_arc_balance(sample_triads)
    print("Arc Health Flags:", flags)
    print("Overall Sanity:", evaluate_overall_sanity(flags))
    print("Issue Summary:", summarize_issues(flags))
