# File: triad_controller.py

from PySide6.QtWidgets import QRadioButton, QPushButton
from typing import List, Dict
from intake.arc_struct import ARC_ORDER
from phases.inception_phase import InceptionPhaseProcessor
from phases.identity_phase import IdentityPhaseProcessor
from phases.input_phase import InputPhaseProcessor
from pipelines.modifier_matrix import ModifierMatrix
from PySide6.QtCore import QTimer
from conductor_engine import ConductorEngine  # make sure conductor_engine.py is importable
# Add import at the top
from triadic_evaluator import TriadicEvaluatorEngine


class TriadController:
    def __init__(self, ui, controller):
        self.ui = ui
        self.controller = controller
        self.selected_arc_index = 0  # default to first arc

        # Arc radio buttons
        self.arc_buttons = [
            self.ui.firstArcRB,
            self.ui.secondArcRB,
            self.ui.thirdArcRB,
            self.ui.fourthArcRB,
            self.ui.fifthArcRB,
            self.ui.sixthArcRB,
            self.ui.seventhArcRB,
        ]

        # Initialize middle agent evaluator
        self.triadic_evaluator = TriadicEvaluatorEngine()


        # 🚀 Initialize Conductor Engine
        self.conductor_engine = ConductorEngine()
        QTimer.singleShot(0, lambda: self.arc_buttons[0].setChecked(True))

        # Bind each button to arc selection with correct index capture
        for idx, button in enumerate(self.arc_buttons):
            button.toggled.connect(self._make_arc_callback(idx))


        # Compute buttons
        self.ui.computeFirstTriadBtn.clicked.connect(self.compute_first_triadic_pairing)
        self.ui.computeSecondTriadBtn.clicked.connect(self.compute_second_triadic_pairing)
        self.ui.computeThirdTriadBtn.clicked.connect(self.compute_third_triadic_pairing)

    def _make_arc_callback(self, index):
        return lambda checked: self.select_arc(index) if checked else None

    def select_arc(self, index: int):
        arc = ARC_ORDER[index]
        self.selected_arc_index = index
        print(f"🔘 Arc {index + 1} selected → {arc}")

    def compute_first_triadic_pairing(self):
        self._compute_and_append("input", InputPhaseProcessor)

    def compute_second_triadic_pairing(self):
        self._compute_and_append("identity", IdentityPhaseProcessor)

    def compute_third_triadic_pairing(self):
        self._compute_and_append("inception", InceptionPhaseProcessor)

    
    def _compute_and_append(self, phase: str, processor):
        arc = ARC_ORDER[self.selected_arc_index]
        print(f"🧠 Computing {phase.upper()} triadic pairing for: {arc}")

        template_data = self.controller.template_data
        rank_map = self.controller.get_priority_map_from_gui()
        print(f"📊 Using rank map: {rank_map}")

        matrix = ModifierMatrix(template_data)

        # Sanity check
        if not template_data or "transforms" not in template_data:
            print("❌ No valid template data. Cannot proceed.")
            return

        if not any(rank_map.values()):
            print("⚠️ All rank values are zero or missing.")

        arc = ARC_ORDER[self.selected_arc_index]
        print(f"🧠 Computing {phase.upper()} triadic pairing for: {arc}")

        template_data = self.controller.template_data
        rank_map = self.controller.get_priority_map_from_gui()
        matrix = ModifierMatrix(template_data)

        if phase == "input":
            triads = processor(matrix).build_input_triads(rank_map)
        elif phase == "identity":
            triads = processor(matrix).build_identity_triads(rank_map)
        elif phase == "inception":
            triads = processor(matrix).build_inception_triads(rank_map)
        else:
            print(f"❌ Unknown phase '{phase}'")
            return

        if not triads:
            print(f"❌ No triads were returned for phase: {phase}")
            return

        if arc.lower() in triads:
            self.controller.append_triads_to_rank_textedit(arc, triads[arc.lower()], phase)
        else:
            print(f"❌ Arc '{arc}' not found in {phase} triads.")



    def compute_final_arc_mo(self):
        arc = ARC_ORDER[self.selected_arc_index]
        rank_map = self.controller.get_priority_map_from_gui()
        rank = rank_map.get(arc, 0)

        if rank == 0:
            print(f"⚠️ No valid rank found for arc: {arc}")
            return

        arc_inputs = self.controller.get_arc_inputs_per_phase(arc)

        if len(arc_inputs) != 3:
            print(f"❌ Missing phase data for arc: {arc}. Got: {arc_inputs}")
            return

        # Middle agent recombination logic
        triad_elements = {
            "input": {"element": arc_inputs["input"]["element"]},
            "identity": {"element": arc_inputs["identity"]["element"]},
            "inception": {"element": arc_inputs["inception"]["element"]}
        }

        result = self.triadic_evaluator.evaluate_permutations(triad_elements)
        selected_mapping = result["best_mapping"]
        trace = result["trace"]

        # Update arc_inputs with selected R/R/R weights
        for phase in ["input", "identity", "inception"]:
            arc_inputs[phase]["weight"] = selected_mapping[phase]["weight"]

        # Pass weighted triad to Conductor
        mo_summary = self.conductor_engine.compute_final_arc_mo(arc_name=arc, triad_data=arc_inputs)

        # Append symbolic trace to summary (for GUI + audit)
        mo_summary["trace"] = trace

        # Output to GUI
        self.controller.append_final_mo_to_output(arc, mo_summary)


    def run_conductor_for_all_arcs(self):
        """
        Compute final M.O. summaries for all 7 rhetorical arcs using stored triad data.
        Appends results to output fields based on each arc's ranking.
        """
        rank_map = self.controller.get_priority_map_from_gui()
        triad_data = self.controller.get_all_arc_inputs()  # expects dict of 7 arcs × 3 phase triads

        if not triad_data:
            print("❌ No triadic data available.")
            return

        for arc_name in ARC_ORDER:
            rank = rank_map.get(arc_name, 0)
            if rank == 0:
                print(f"⚠️ Skipping arc '{arc_name}' — no rank assigned.")
                continue

            arc_triads = triad_data.get(arc_name, {})
            if not arc_triads or len(arc_triads) != 3:
                print(f"❌ Missing triad inputs for arc: {arc_name}")
                continue

            triad_elements = {
                "input": {"element": arc_triads["input"]["element"]},
                "identity": {"element": arc_triads["identity"]["element"]},
                "inception": {"element": arc_triads["inception"]["element"]}
            }

            result = self.triadic_evaluator.evaluate_permutations(triad_elements)
            selected_mapping = result["best_mapping"]
            trace = result["trace"]

            for phase in ["input", "identity", "inception"]:
                triad_data = arc_triads.get(phase, {})
                triad_data["weight"] = selected_mapping[phase]["weight"]

            mo_summary = self.conductor_engine.compute_final_arc_mo(
                arc_name=arc_name,
                triad_data=arc_triads
            )

            mo_summary["trace"] = trace


            self.controller.append_final_mo_to_output(arc_name, mo_summary)
            print(f"✅ M.O. summary computed for {arc_name} → rank {rank}")

    def get_all_arc_inputs(self) -> dict:
        """
        Retrieves all triadic data for all 7 arcs across input, identity, and inception phases.
        
        Returns:
            dict: {
                "Essence": {"input": {...}, "identity": {...}, "inception": {...}},
                "Form": {...},
                ...
            }
        """
        arc_inputs = {}

        arc_names = [
            "Essence",
            "Form",
            "Function",
            "Context",
            "Intent",
            "Relation",
            "Value"
        ]

        for arc in arc_names:
            arc_data = self.controller.get_arc_inputs_per_phase(arc)
            if arc_data and len(arc_data) == 3:
                arc_inputs[arc] = arc_data
            else:
                print(f"⚠️ Incomplete triad data for arc: {arc}")

        return arc_inputs
