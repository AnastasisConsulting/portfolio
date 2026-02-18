# File: conductor_engine.py

class ConductorEngine:
    def __init__(self):
        # Initialize a structure to hold each arc's final M.O. (Mode of Operation) summary
        self.arc_mo_summaries = {}  # {arc_name: mo_summary_text}

        # Initialize a structure to log Risk/Reward/Relation weights per arc
        self.arc_weight_log = {}  # {arc_name: {'risk': value, 'reward': value, 'relation': value}}

    def compute_final_arc_mo(self, arc_name: str, triad_data: dict) -> dict:
        """
        Synthesizes the final M.O. summary for a given arc based on its triad data.

        Returns:
            dict: {
                'arc': arc_name,
                'input': {...},
                'identity': {...},
                'inception': {...},
                'summary': synthesis string,
            }
        """

        input_element = triad_data['input']['element']
        identity_element = triad_data['identity']['element']
        inception_element = triad_data['inception']['element']

        input_weight = triad_data['input']['weight']
        identity_weight = triad_data['identity']['weight']
        inception_weight = triad_data['inception']['weight']

        self.arc_weight_log[arc_name] = {
            'risk': 1 if input_weight == 'Risk' else 0,
            'reward': 1 if identity_weight == 'Reward' else 0,
            'relation': 1 if inception_weight == 'Relation' else 0,
        }

        mo_summary = (
            f"Through {input_element}, shaped by {identity_element}, and resolved via {inception_element}, "
            f"the arc of {arc_name} seeks {self._resolve_mo_bias(input_weight, identity_weight, inception_weight)}."
        )

        self.arc_mo_summaries[arc_name] = mo_summary

        return {
            "arc": arc_name,
            "input": triad_data["input"],
            "identity": triad_data["identity"],
            "inception": triad_data["inception"],
            "summary": mo_summary
        }

    def _resolve_mo_bias(self, input_weight: str, identity_weight: str, inception_weight: str) -> str:
        """
        Determine dominant motivational bias (Risk, Reward, Relation) based on weight patterns.
        """

        weights = [input_weight, identity_weight, inception_weight]
        if weights.count('Risk') >= 2:
            return "security amidst uncertainty"
        elif weights.count('Reward') >= 2:
            return "attainment of transformative gains"
        elif weights.count('Relation') >= 2:
            return "harmonious synthesis of forces"
        else:
            return "a balanced realization of intent"

    def get_arc_summary(self, arc_name: str) -> str:
        """
        Retrieve the synthesized M.O. summary for a given arc.
        """
        return self.arc_mo_summaries.get(arc_name, "")

    def get_all_summaries(self) -> dict:
        """
        Retrieve all arc M.O. summaries at once.
        """
        return self.arc_mo_summaries

    def get_arc_weights(self, arc_name: str) -> dict:
        """
        Retrieve Risk/Reward/Relation weights for a specific arc.
        """
        return self.arc_weight_log.get(arc_name, {'risk': 0, 'reward': 0, 'relation': 0})

    def get_all_weights(self) -> dict:
        """
        Retrieve weight logs for all arcs.
        """
        return self.arc_weight_log
