import os
import json

BASE = "demos/tavern_memory_demo"

main_py = '''
import sys
from PySide6.QtWidgets import QApplication
from tavern_gui import TavernWindow

sys.path.append("../../")  # Access parent engine
from synthesis_engine import run_synthesis_from_ui
from pipelines.transform_loader import TransformLoader
from trililiquarium_manager import TrililiquariumManager

def tavern_engine_handler(user_input, character_name, memory_context):
    template_data = TransformLoader().load()  # Uses the default from the engine root
    controller = TrililiquariumManager.get().initialize(ui=None, template_data=template_data)

    controller.get_priority_map_from_gui = lambda: {
        "essence": 1, "form": 2, "action": 3, "frame": 4,
        "intent": 5, "relation": 6, "value": 7
    }

    combined_prompt = f"Memory so far:\\n{memory_context}\\n\\nYou now say: {user_input}"

    controller.template_data["manual_arcs"] = {
        "essence": f"The mood shifts as {character_name} speaks.",
        "form": character_name,
        "action": "Words ripple across the table.",
        "frame": "Inside the Whispering Flask tavern",
        "intent": combined_prompt,
        "relation": "All listen in silence...",
        "value": "The night deepens."
    }

    result = run_synthesis_from_ui(controller)
    return result.get("final_output", "[No Output]")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TavernWindow(synthesis_callback=tavern_engine_handler)
    window.show()
    sys.exit(app.exec())
'''

tavern_gui_py = '''
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QTextEdit, QPushButton,
    QLabel, QVBoxLayout, QListWidget, QListWidgetItem
)

CHARACTERS = {
    "Seat 1": "Old knight nursing a bitter ale",
    "Seat 2": "Quiet mage flipping a red-jacketed tome",
    "Seat 3": "Drunken bard humming softly",
    "Seat 4": "Merchant counting foreign coins",
    "Bar":    "Barkeep polishing a chipped mug"
}

class TavernWindow(QMainWindow):
    def __init__(self, synthesis_callback):
        super().__init__()
        self.setWindowTitle("Tavern Encounter")
        self.resize(800, 600)
        self.synthesis_callback = synthesis_callback
        self.memory_log = {name: [] for name in CHARACTERS}

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        intro = QLabel("🍻 You enter a dimly-lit tavern. Five figures await conversation.")
        layout.addWidget(intro)

        self.seat_list = QListWidget()
        for seat, desc in CHARACTERS.items():
            item = QListWidgetItem(f"{seat} — {desc}")
            self.seat_list.addItem(item)
        layout.addWidget(self.seat_list)

        self.story_output = QTextEdit()
        self.story_output.setReadOnly(True)
        layout.addWidget(self.story_output)

        self.user_input = QTextEdit()
        self.user_input.setPlaceholderText("Say something to continue the story...")
        layout.addWidget(self.user_input)

        self.send_btn = QPushButton("Speak")
        self.send_btn.clicked.connect(self.send_to_engine)
        layout.addWidget(self.send_btn)

    def send_to_engine(self):
        item = self.seat_list.currentItem()
        if not item:
            self.story_output.append("⚠️ Please choose a character to talk to.")
            return

        char_label = item.text().split(" — ")[0]
        user_text = self.user_input.toPlainText().strip()
        if not user_text:
            return

        self.memory_log[char_label].append(f"You said: {user_text}")
        full_memory = self._gather_group_memory()

        self.story_output.append(f"\\n🗣 You to {char_label}: {user_text}")
        self.user_input.clear()

        response = self.synthesis_callback(user_text, char_label, full_memory)
        self.story_output.append(f"\\n🎭 Response: {response}")

    def _gather_group_memory(self) -> str:
        memory_lines = []
        for who, logs in self.memory_log.items():
            if logs:
                memory_lines.append(f"{who} Memory:\\n" + "\\n".join(logs))
        return "\\n\\n".join(memory_lines)
'''

default_transform = {
    "transforms": [
        {
            "name": "Input Transform",
            "modifiers": [{"name": "Mod A", "elements": [""]*7},
                          {"name": "Mod B", "elements": [""]*7},
                          {"name": "Mod C", "elements": [""]*7}]
        },
        {
            "name": "Identity Transform",
            "modifiers": [{"name": "Mod A", "elements": [""]*7},
                          {"name": "Mod B", "elements": [""]*7},
                          {"name": "Mod C", "elements": [""]*7}]
        },
        {
            "name": "Inception Transform",
            "modifiers": [{"name": "Mod A", "elements": [""]*7},
                          {"name": "Mod B", "elements": [""]*7},
                          {"name": "Mod C", "elements": [""]*7}]
        }
    ]
}

def write_demo_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"✅ {path}")

def setup_tavern_demo():
    # ✅ Make the directory before opening the file
    os.makedirs(f"{BASE}/transforms", exist_ok=True)

    write_demo_file(f"{BASE}/main.py", main_py)
    write_demo_file(f"{BASE}/tavern_gui.py", tavern_gui_py)

    # ✅ Now write the JSON safely
    with open(f"{BASE}/transforms/default_transform_template.json", "w", encoding="utf-8") as f:
        json.dump(default_transform, f, indent=2)

    print(f"✅ {BASE}/transforms/default_transform_template.json")


if __name__ == "__main__":
    setup_tavern_demo()
