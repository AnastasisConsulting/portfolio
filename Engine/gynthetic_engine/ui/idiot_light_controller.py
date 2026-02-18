from typing import Dict

class IdiotLightController:
    def __init__(self, ui_reference):
        self.ui = ui_reference  # Expected to have arc-labeled light widgets (e.g. QLabel or QPushButton)

    def update_lights(self, arc_flags: Dict[str, str]):
        """
        Update UI elements (lights) based on arc sanity status.
        arc_flags: Dict[arc_name → 'green' | 'yellow' | 'red']
        """
        for arc, status in arc_flags.items():
            light_widget = getattr(self.ui, f"{arc}_light", None)
            if light_widget:
                color = self._status_to_color(status)
                tooltip = self._status_tooltip(arc, status)
                light_widget.setStyleSheet(f"background-color: {color}; border-radius: 6px;")
                light_widget.setToolTip(tooltip)

    def _status_to_color(self, status: str) -> str:
        if status == "green":
            return "#4CAF50"  # Green
        elif status == "yellow":
            return "#FFC107"  # Amber
        elif status == "red":
            return "#F44336"  # Red
        else:
            return "#9E9E9E"  # Grey (unknown)

    def _status_tooltip(self, arc: str, status: str) -> str:
        descriptions = {
            "green": "✓ Arc structure is healthy and complete.",
            "yellow": "⚠ Arc is underdeveloped or sparsely populated.",
            "red": "✖ Arc is malformed or missing — risk of epistemic failure."
        }
        return f"{arc.title()} Arc: {descriptions.get(status, 'Unknown status.')}"