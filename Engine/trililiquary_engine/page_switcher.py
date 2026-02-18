# page_switcher.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, QTimer


class DebugPageSwitcher(QWidget):
    def __init__(self, ui, parent=None):
        super().__init__(None)  # not parented to your main window
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)

        self.ui = ui
        self.page_names = [
            "Dashboard",
            "LLM Config",
            "Template Editor",
            "Trililiquarium",
            "Trace Audits"
        ]

        self.setWindowTitle("Debug: Page Switcher")
        self.setFixedSize(200, 250)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        for i, name in enumerate(self.page_names):
            btn = QPushButton(f"{i}: {name}")
            btn.clicked.connect(lambda _, index=i: self.switch_to_page(index))
            layout.addWidget(btn)

        self.setLayout(layout)

        # Delay show + raise for post-launch activation
        QTimer.singleShot(200, self.force_raise)

    def switch_to_page(self, index: int):
        self.ui.mainStackedWidget.setCurrentIndex(index)
        print(f"🔀 Switched to {self.page_names[index]} (index {index})")

    def force_raise(self):
        self.show()
        self.raise_()
        self.activateWindow()

