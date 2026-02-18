from PySide6.QtWidgets import QWidget, QDialog
from ui.gpt2 import Ui_IOGB

class GPT2FloatingWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_IOGB()
        self.ui.setupUi(self)
        self.setWindowTitle("GPT2 Console")
        self.setFixedSize(400, 600)  # Adjust as needed
        self._connect_signals()

    def _connect_signals(self):
        self.ui.sendBtn.clicked.connect(self.handle_send)
        self.ui.cancelBn.clicked.connect(self.handle_cancel)

    def handle_send(self):
        user_text = self.ui.userInputTextEdit.toPlainText()
        self.ui.gptResponseWindow.append(f"[USER]: {user_text}")
        self.ui.userInputTextEdit.clear()

    def handle_cancel(self):
        self.ui.userInputTextEdit.clear()
