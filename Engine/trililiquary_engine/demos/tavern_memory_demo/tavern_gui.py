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

        self.story_output.append(f"\n🗣 You to {char_label}: {user_text}")
        self.user_input.clear()

        response = self.synthesis_callback(user_text, char_label, full_memory)
        self.story_output.append(f"\n🎭 Response: {response}")

    def _gather_group_memory(self) -> str:
        memory_lines = []
        for who, logs in self.memory_log.items():
            if logs:
                memory_lines.append(f"{who} Memory:\n" + "\n".join(logs))
        return "\n\n".join(memory_lines)