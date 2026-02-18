# Auto-generated placeholder
from typing import List
from PySide6.QtWidgets import QWidget, QLabel

class PipelineRankController:
    def __init__(self, ui):
        self.ui = ui

    def get_ranked_pipeline_ids(self) -> List[str]:
        """
        Extracts pipeline priority from the drag-and-drop stack.
        Each QLabel in the pillarRanksWidget is expected to contain text like "Pipeline 3".
        Returns a list of pipeline IDs in ranked order.
        """
        container: QWidget = self.ui.pillarRanksWidget
        layout = container.layout()

        ranked_pipelines = []
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QLabel):
                label_text = widget.text().strip().lower()
                if label_text.startswith("pipeline"):
                    pipeline_id = label_text.replace(" ", "_")
                    ranked_pipelines.append(pipeline_id)

        return ranked_pipelines

    def debug_print_rank_order(self):
        ranked = self.get_ranked_pipeline_ids()
        print("\nPipeline priority order (highest → lowest):")
        for i, p in enumerate(ranked):
            print(f"Rank {i+1}: {p}")
