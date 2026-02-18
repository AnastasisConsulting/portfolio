# arc_struct.py

from dataclasses import dataclass
from typing import Dict, List

# Canonical Arc Order (used for ordering, radio buttons, synthesis, etc.)
ARC_ORDER: List[str] = [
    "essence",
    "form",
    "action",
    "frame",
    "intent",
    "relation",
    "value"
]

# Mapping to pipeline identifiers (pipeline_1 through pipeline_7)
ARC_TO_PIPELINE_ID: Dict[str, str] = {
    arc: f"pipeline_{i+1}" for i, arc in enumerate(ARC_ORDER)
}

PIPELINE_ID_TO_ARC: Dict[str, str] = {
    v: k for k, v in ARC_TO_PIPELINE_ID.items()
}

# Optional descriptions for tooltips / exports
ARC_DESCRIPTIONS: Dict[str, str] = {
    "essence":  "What it is: the intrinsic identity of the thing.",
    "form":     "How it appears: shape, logic, or structure.",
    "action":   "What it does or enables.",
    "frame":    "When and where: context or bounds.",
    "intent":   "Why it exists: purpose or direction.",
    "relation": "How it connects or interacts with others.",
    "value":    "What it means or is worth."
}

@dataclass
class RhetoricalArcs:
    essence: str
    form: str
    action: str
    frame: str
    intent: str
    relation: str
    value: str

    def to_dict(self) -> dict:
        return {
            "essence": self.essence,
            "form": self.form,
            "action": self.action,
            "frame": self.frame,
            "intent": self.intent,
            "relation": self.relation,
            "value": self.value
        }

    @staticmethod
    def from_dict(data: dict) -> "RhetoricalArcs":
        return RhetoricalArcs(
            essence=data.get("essence", ""),
            form=data.get("form", ""),
            action=data.get("action", ""),
            frame=data.get("frame", ""),
            intent=data.get("intent", ""),
            relation=data.get("relation", ""),
            value=data.get("value", "")
        )
