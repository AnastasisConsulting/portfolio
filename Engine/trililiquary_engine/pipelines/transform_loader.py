# Auto-generated placeholder
import json
from pathlib import Path
from typing import Dict

DEFAULT_TEMPLATE_PATH = Path("transforms/default_transform_template.json")

class TransformLoader:
    def __init__(self, filepath: Path = DEFAULT_TEMPLATE_PATH):
        self.filepath = filepath

    def load(self) -> Dict:
        if not self.filepath.exists():
            raise FileNotFoundError(f"Transform template not found at: {self.filepath}")

        with self.filepath.open("r") as f:
            data = json.load(f)

        if "transforms" not in data or not isinstance(data["transforms"], list):
            raise ValueError("Invalid template format: missing 'transforms' list")

        return data

    def save(self, data: Dict):
        with self.filepath.open("w") as f:
            json.dump(data, f, indent=2)
        print(f"Template saved to {self.filepath}")
