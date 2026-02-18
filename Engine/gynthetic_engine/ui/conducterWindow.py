from PySide6.QtWidgets import QWidget, QMessageBox
from ui.composer import Ui_Form  # Reuse same UI Form structure
from ui.assistant_creator import create_and_save_assistant
from dotenv import set_key
from pathlib import Path
from utils.env_writer import write_env_file

class ConductorWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowTitle("Conductor Assistant Builder")

        # Button wiring
        self.ui.composerAPI_SaveBtn.clicked.connect(self.on_save_conductor)
        self.ui.updateBtn.clicked.connect(self.update_config)
        self.ui.cancelBtn.clicked.connect(self.close)

    def on_save_conductor(self):
        api_key = self.ui.outputLLM_API_KeyLE.text().strip()
        name = self.ui.agentNameLE.text().strip()
        prompt = self.ui.systemPromptTE.toPlainText().strip()

        if not api_key:
            QMessageBox.critical(self, "Missing API Key", "Please enter your OpenAI API key.")
            return

        if not name or not prompt:
            QMessageBox.warning(self, "Incomplete Fields", "Please enter both name and prompt.")
            return

        try:
            assistant_id = create_and_save_assistant(api_key, "conductor", name, prompt)
            self.ui.agentID_LE.setText(assistant_id)
            QMessageBox.information(self, "Success", f"Assistant created and saved: {assistant_id}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create assistant: {e}")

    def update_config(self):
        api_key = self.ui.outputLLM_API_KeyLE.text().strip()
        name = self.ui.agentNameLE.text().strip()
        assistant_id = self.ui.agentID_LE.text().strip()

        if not api_key or not assistant_id:
            QMessageBox.critical(self, "Missing Data", "You must enter both API key and Agent ID.")
            return

        env_path = Path("secrets/conductor.env")
        write_env_file(env_path, {
            "OPENAI_API_KEY": api_key,
            "CONDUCTOR_ID": assistant_id,
            "CONDUCTOR_NAME": name or "Unnamed"
        })

        QMessageBox.information(self, "Updated", "✅ Conductor assistant configuration updated.")
        if self.parent():
            self.parent().refresh_conductor_assistant()
