# synthesis_engine.py

from typing import Dict
from intake.arc_struct import ARC_ORDER
from pipelines.modifier_matrix import ModifierMatrix
from phases.input_phase import InputPhaseProcessor
from phases.identity_phase import IdentityPhaseProcessor
from phases.inception_phase import InceptionPhaseProcessor
from intake.sanity_checker import check_arc_balance, evaluate_overall_sanity, summarize_issues
from pipelines.triad_assembler import assemble_triads
from assembly.triadic_output_builder import build_prompt_stack
from output.output_llm_bridge import synthesize_output


def run_synthesis_from_ui(controller, ui=None) -> Dict[str, str]:
    """
    Executes the full 3-phase triadic transformation and synthesis pipeline
    using data from TrililiquariumController and optionally updates the UI.

    Args:
        controller: TrililiquariumController
        ui: optional Ui_MainWindow if you want to push output into GUI fields

    Returns:
        Dictionary containing:
            - final_output
            - triads_by_arc
            - arc_flags
            - sanity
            - issues
    """
    transform_data = controller.template_data
    arc_ranks = controller.get_priority_map_from_gui()

    matrix = ModifierMatrix(transform_data)

    input_triads = InputPhaseProcessor(matrix).build_input_triads(arc_ranks)
    identity_triads = IdentityPhaseProcessor(matrix).build_identity_triads(arc_ranks)
    inception_triads = InceptionPhaseProcessor(matrix).build_inception_triads(arc_ranks)

    triads_by_arc = {
        arc: [input_triads[arc], identity_triads[arc], inception_triads[arc]]
        for arc in ARC_ORDER
    }

    arc_flags = check_arc_balance(triads_by_arc)
    sanity = evaluate_overall_sanity(arc_flags)
    issues = summarize_issues(arc_flags)

    # If using drag-drop override, you could pull from: PipelineRankController(ui).get_ranked_pipeline_ids()
    ranked_pipeline_ids = [f"pipeline_{i+1}" for i in range(7)]

    prompt_stack = build_prompt_stack(triads_by_arc, ranked_pipeline_ids)
    final_output = synthesize_output(prompt_stack)

    if ui:
        # Optional UI update: show result in summary field
        if hasattr(ui, "synthesisResultTE"):
            ui.synthesisResultTE.setPlainText(final_output)

        if hasattr(ui, "sanitySummaryTE"):
            ui.sanitySummaryTE.setPlainText(f"Sanity: {sanity}\nIssues:\n" + "\n".join(issues))

    return {
        "final_output": final_output,
        "triads_by_arc": triads_by_arc,
        "arc_flags": arc_flags,
        "sanity": sanity,
        "issues": issues,
        "prompt_stack": prompt_stack
    }
