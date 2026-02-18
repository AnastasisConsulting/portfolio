# ui/enter_key_filter.py

from PySide6.QtCore import QObject, QEvent, Qt

class EnterKeyFilter(QObject):
    def __init__(self, send_callback):
        super().__init__()
        self.send_callback = send_callback

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Return:
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                return False  # Allow Shift+Enter to add newline
            self.send_callback()
            return True
        return False
