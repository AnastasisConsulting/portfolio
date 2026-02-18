from pathlib import Path
import json

# 1) requirements.txt update
req_path = Path("/mnt/data/requirements.txt")
if req_path.exists():
    existing = req_path.read_text()
else:
    existing = ""
needed = "requests>=2.31.0\nPySide6>=6.7.0\n"
if "requests" not in existing:
    existing += ("\n" if existing and not existing.endswith("\n") else "") + "requests>=2.31.0\n"
if "PySide6" not in existing:
    existing += ("PySide6>=6.7.0\n" if not existing.endswith("PySide6>=6.7.0\n") else "")
req_path.write_text(existing)

# 2) llm_bridge.py
llm_bridge_code = r'''
import os
import json
import requests

class LLMClient:
    """
    Lightweight client that supports three provider styles:
    - "ollama": local http://localhost:11434/api/chat (no key required)
    - "openai-compatible": POST {base_url}/v1/chat/completions (LM Studio, some proxies)
    - "huggingface": POST https://api-inference.huggingface.co/models/{model}
    """
    def __init__(self, provider="ollama", model="phi3:mini", base_url=None, api_key=None, timeout=120):
        self.provider = provider
        self.model = model
        self.base_url = base_url
        self.api_key = api_key or os.getenv("API_KEY", None)
        self.timeout = timeout

    def chat(self, system_prompt=None, user_prompt=None, messages=None, temperature=0.7, max_tokens=800):
        if messages is None:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            if user_prompt:
                messages.append({"role": "user", "content": user_prompt})

        if self.provider == "ollama":
            return self._chat_ollama(messages, temperature, max_tokens)
        elif self.provider == "openai-compatible":
            return self._chat_openai_compatible(messages, temperature, max_tokens)
        elif self.provider == "huggingface":
            return self._chat_huggingface("\n".join([m.get("content","") for m in messages]), temperature, max_tokens)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    # --- Providers ---
    def _chat_ollama(self, messages, temperature, max_tokens):
        url = (self.base_url or "http://localhost:11434") + "/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens}
        }
        r = requests.post(url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        # expected: {"message":{"role":"assistant","content":"..."}, "done": true, ...}
        msg = data.get("message", {})
        return msg.get("content", data.get("response", ""))  # fallback to /api/generate style

    def _chat_openai_compatible(self, messages, temperature, max_tokens):
        base = self.base_url or "http://localhost:1234"
        url = base.rstrip("/") + "/v1/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        r = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        # expected OpenAI format
        return data["choices"][0]["message"]["content"]

    def _chat_huggingface(self, prompt, temperature, max_tokens):
        if not self.api_key:
            raise ValueError("Hugging Face requires an API key. Set api_key or HF_TOKEN env var.")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        url = (self.base_url or "https://api-inference.huggingface.co") + f"/models/{self.model}"
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": max_tokens, "temperature": temperature},
            "options": {"wait_for_model": True}
        }
        r = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        # data can be [{"generated_text": "..."}] or dicts depending on pipeline
        if isinstance(data, list) and data and "generated_text" in data[0]:
            return data[0]["generated_text"]
        # Some text-gen models return a single string
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"]
        # Last resort
        return json.dumps(data)

Path("/mnt/data/llm_bridge.py").write_text(llm_bridge_code)

# 3) gsynthetic_gui_llm.py (GUI variant with LLM settings + "Synthesize" button)
gui_llm_code = r'''
import sys
import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QFileDialog, QMessageBox,
    QComboBox, QPushButton, QLabel, QTextEdit, QTableWidget, QTableWidgetItem,
    QTabWidget, QFormLayout, QLineEdit, QSpinBox, QStatusBar
)



# Reuse utility bits from the previous GUI implementation (embedded here for self-containment)
R_ARCS = ["Essence", "Form", "Function", "Context", "Intent", "Relation", "Value"]
PHASE_DEFAULTS = ["Input", "Expansion", "Nuance"]
PHASE_ALIASES = {"Identity": "Expansion", "Inception": "Nuance"}

def coerce_phases(transforms: dict):
    mapped = {}
    for k, v in transforms.items():
        canonical = PHASE_ALIASES.get(k, k)
        mapped[canonical] = v
    return mapped

def collect_modifiers(transforms: dict):
    mods = set()
    for phase, content in transforms.items():
        if isinstance(content, dict):
            for mod in content.keys():
                mods.add(mod)
    return sorted(mods)

def assemble_layer_triads(template: dict, modifiers_by_phase: dict):
    transforms = coerce_phases(template.get("transforms", {}))
    phase_lists = {}
    for phase in PHASE_DEFAULTS:
        phase_data = transforms.get(phase, {})
        mod = modifiers_by_phase.get(phase, None)
        if not mod or mod not in phase_data:
            raise ValueError(f"Missing or unknown modifier '{mod}' for phase '{phase}'")
        items = phase_data[mod]
        if not isinstance(items, list) or len(items) < 7:
            raise ValueError(f"Phase '{phase}' modifier '{mod}' must be a list with at least 7 items")
        phase_lists[phase] = items

    layers = []
    for i, arc in enumerate(R_ARCS):
        triad = [phase_lists["Input"][i], phase_lists["Expansion"][i], phase_lists["Nuance"][i]]
        summary = f"{triad[0]} → {triad[1]} → {triad[2]}"
        layers.append({"layer": i+1, "arc": arc, "triad": triad, "summary": summary})
    return layers

class TemplateExplorer(QWidget):
    def __init__(self):
        super().__init__()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Template", "Value"])
        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        self.setLayout(layout)

    def load_template(self, data: dict):
        self.tree.clear()
        root = QTreeWidgetItem(["name", str(data.get("name", "unnamed"))])
        self.tree.addTopLevelItem(root)
        transforms = coerce_phases(data.get("transforms", {}))
        t_item = QTreeWidgetItem(["transforms", ""]); root.addChild(t_item)
        for phase, content in transforms.items():
            p_item = QTreeWidgetItem([phase, ""]); t_item.addChild(p_item)
            if isinstance(content, dict):
                for mod, items in content.items():
                    m_item = QTreeWidgetItem([mod, f"{len(items)} items"]); p_item.addChild(m_item)
                    if isinstance(items, list):
                        for idx, val in enumerate(items):
                            m_item.addChild(QTreeWidgetItem([f"[{idx}]", str(val)]))
        self.tree.expandAll()

class IntakeTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.raw_input = QTextEdit(); self.raw_input.setPlaceholderText("Enter your raw input / prompt context...")
        layout.addWidget(QLabel("Raw Intake")); layout.addWidget(self.raw_input)

        self.arc_fields = []
        grid = QGridLayout()
        for i, arc in enumerate(R_ARCS):
            grid.addWidget(QLabel(arc), i, 0)
            te = QLineEdit(); te.setPlaceholderText(f"{arc} (optional)")
            self.arc_fields.append(te)
            grid.addWidget(te, i, 1)
        layout.addWidget(QLabel("Rhetorical Arc Decomposition")); layout.addLayout(grid)
        self.setLayout(layout)

    def export_arcs(self):
        return {arc: self.arc_fields[i].text() for i, arc in enumerate(R_ARCS)}

class PipelineTab(QWidget):
    def __init__(self):
        super().__init__()
        outer = QVBoxLayout()
        form = QFormLayout()
        self.mod_input = QComboBox(); self.mod_expansion = QComboBox(); self.mod_nuance = QComboBox()
        form.addRow("Input Modifier", self.mod_input)
        form.addRow("Expansion Modifier", self.mod_expansion)
        form.addRow("Nuance Modifier", self.mod_nuance)
        outer.addLayout(form)

        btn_row = QHBoxLayout()
        self.assemble_btn = QPushButton("Assemble Triads")
        btn_row.addWidget(self.assemble_btn)
        outer.addLayout(btn_row)

        self.table = QTableWidget(7, 4)
        self.table.setHorizontalHeaderLabels(["Arc", "Input", "Expansion", "Nuance"])
        for i, arc in enumerate(R_ARCS): self.table.setItem(i, 0, QTableWidgetItem(arc))
        outer.addWidget(self.table)
        self.setLayout(outer)

    def set_modifiers(self, modifiers):
        for box in (self.mod_input, self.mod_expansion, self.mod_nuance):
            box.clear(); [box.addItem(m) for m in modifiers]

    def get_modifiers_by_phase(self):
        return {"Input": self.mod_input.currentText(), "Expansion": self.mod_expansion.currentText(), "Nuance": self.mod_nuance.currentText()}

    def populate_triads(self, layers):
        for i, L in enumerate(layers):
            tri = L["triad"]
            self.table.setItem(i, 1, QTableWidgetItem(str(tri[0])))
            self.table.setItem(i, 2, QTableWidgetItem(str(tri[1])))
            self.table.setItem(i, 3, QTableWidgetItem(str(tri[2])))

class OutputTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # LLM settings
        settings = QFormLayout()
        self.provider = QComboBox(); self.provider.addItems(["ollama", "openai-compatible", "huggingface"])
        self.base_url = QLineEdit(); self.base_url.setPlaceholderText("http://localhost:11434 (ollama) or http://localhost:1234 (LM Studio)")
        self.model = QLineEdit(); self.model.setPlaceholderText("phi3:mini (ollama), local-model, or hf/model-id")
        self.api_key = QLineEdit(); self.api_key.setPlaceholderText("API key (if required)")
        self.temp = QSpinBox(); self.temp.setRange(0, 100); self.temp.setValue(7)   # x10 for 0.7
        self.max_tokens = QSpinBox(); self.max_tokens.setRange(16, 4096); self.max_tokens.setValue(800)

        settings.addRow("Provider", self.provider)
        settings.addRow("Base URL", self.base_url)
        settings.addRow("Model", self.model)
        settings.addRow("API Key", self.api_key)
        settings.addRow("Temperature (x10)", self.temp)
        settings.addRow("Max Tokens", self.max_tokens)

        layout.addLayout(settings)

        # Generated scaffold + synthesize
        self.output_scaffold = QTextEdit(); self.output_scaffold.setReadOnly(True)
        layout.addWidget(QLabel("Scaffold JSON (from Pipeline)"))
        layout.addWidget(self.output_scaffold)

        synth_row = QHBoxLayout()
        self.build_btn = QPushButton("Build Scaffold from Current Triads")
        self.synth_btn = QPushButton("Synthesize with LLM")
        synth_row.addWidget(self.build_btn); synth_row.addWidget(self.synth_btn)
        layout.addLayout(synth_row)

        self.final_text = QTextEdit()
        layout.addWidget(QLabel("LLM Response"))
        layout.addWidget(self.final_text)

        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("G-ynthetic — GUI + LLM")
        self.resize(1200, 800)
        self.template_data = None
        self._last_layers = None

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.explorer = TemplateExplorer()
        splitter.addWidget(self.explorer)

        self.tabs = QTabWidget()
        self.tab_intake = IntakeTab()
        self.tab_pipeline = PipelineTab()
        self.tab_output = OutputTab()
        self.tabs.addTab(self.tab_intake, "Intake")
        self.tabs.addTab(self.tab_pipeline, "Pipeline")
        self.tabs.addTab(self.tab_output, "Output")
        splitter.addWidget(self.tabs)

        self.setCentralWidget(splitter)
        self.status = QStatusBar(); self.setStatusBar(self.status)

        # Wire buttons
        self.tab_pipeline.assemble_btn.clicked.connect(self.on_assemble)
        self.tab_output.build_btn.clicked.connect(self.on_build_scaffold)
        self.tab_output.synth_btn.clicked.connect(self.on_synthesize)

        # Menus
        self._build_menus()

        # Load default template if present
        demo = Path("templates/demo_template.json")
        if demo.exists():
            self.load_template_from_path(str(demo))

    def _build_menus(self):
        file_menu = self.menuBar().addMenu("&File")
        open_action = file_menu.addAction("Open Template..."); open_action.triggered.connect(self.on_open_template)

    def on_open_template(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Template", ".", "JSON Files (*.json)")
        if path: self.load_template_from_path(path)

    def load_template_from_path(self, path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
            self.template_data = data
            self.explorer.load_template(data)
            mods = collect_modifiers(coerce_phases(data.get("transforms", {})))
            if mods: self.tab_pipeline.set_modifiers(mods)
            self.status.showMessage(f"Loaded template: {Path(path).name}", 4000)
        except Exception as e:
            QMessageBox.critical(self, "Template Error", str(e))

    def on_assemble(self):
        if not self.template_data:
            QMessageBox.warning(self, "No Template", "Load a template first."); return
        mods = self.tab_pipeline.get_modifiers_by_phase()
        try:
            self._last_layers = assemble_layer_triads(self.template_data, mods)
            self.tab_pipeline.populate_triads(self._last_layers)
            self.status.showMessage("Triads assembled.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Assemble Error", str(e))

    def on_build_scaffold(self):
        if not self._last_layers:
            QMessageBox.information(self, "Info", "Assemble triads first."); return
        # Build minimal scaffold
        scaffold = {
            "intake": self.tab_intake.raw_input.toPlainText(),
            "layers": [
                {"rank": L["layer"], "arc": L["arc"], "triad": L["triad"], "summary": L["summary"], "weight": 8 - L["layer"]}
                for L in self._last_layers
            ]
        }
        self.tab_output.output_scaffold.setText(json.dumps(scaffold, indent=2))
        self.status.showMessage("Scaffold built.", 3000)

    def on_synthesize(self):
        try:
            scaffold_text = self.tab_output.output_scaffold.toPlainText().strip()
            if not scaffold_text:
                QMessageBox.information(self, "Info", "Build the scaffold first."); return
            scaffold = json.loads(scaffold_text)

            provider = self.tab_output.provider.currentText()
            base_url = self.tab_output.base_url.text().strip() or None
            model = self.tab_output.model.text().strip() or ("phi3:mini" if provider == "ollama" else "local-model")
            api_key = self.tab_output.api_key.text().strip() or None
            temperature = self.tab_output.temp.value() / 10.0
            max_tokens = self.tab_output.max_tokens.value()

            client = LLMClient(provider=provider, base_url=base_url, model=model, api_key=api_key)

            system_prompt = "You are a reasoning model that composes a final response from a pre-structured cognitive scaffold. Respect layer weights and arc intent."
            user_prompt = (
                "Use the scaffold below to produce a concise, coherent response. "
                "Prioritize lower rank numbers (higher weight). Maintain logical flow.\n\n"
                f"Scaffold JSON:\n{json.dumps(scaffold, indent=2)}"
            )
            reply = client.chat(system_prompt=system_prompt, user_prompt=user_prompt,
                                temperature=temperature, max_tokens=max_tokens)
            self.tab_output.final_text.setText(reply)
            self.status.showMessage("LLM synthesis complete.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "LLM Error", str(e))

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()