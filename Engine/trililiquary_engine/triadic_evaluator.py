# triadic_evaluator.py

import itertools
from typing import Dict, List, Tuple


class TriadicEvaluatorEngine:
    def __init__(self):
        # Optional: allow pluggable scoring logic
        self.role_weights = {
            "Risk": 1.0,
            "Reward": 2.0,
            "Relation": 1.5
        }

    def evaluate_permutations(self, triad: Dict[str, Dict]) -> Dict:
        """
        Given a triad from 3 phases, evaluate all 6 Risk/Reward/Relation mappings
        and return the best scoring assignment with an audit log.

        triad = {
            "input": {"element": "x"},
            "identity": {"element": "y"},
            "inception": {"element": "z"}
        }

        Returns:
            {
                "best_mapping": {phase: {"element": val, "weight": role}},
                "score": float,
                "permutations": [each mapping with score],
                "trace": str (log text)
            }
        """
        phase_keys = ["input", "identity", "inception"]
        role_perms = list(itertools.permutations(["Risk", "Reward", "Relation"]))

        best_score = float("-inf")
        best_mapping = None
        trace_lines = []

        all_results = []

        for perm in role_perms:
            score = 0
            mapping = {}
            line = []

            for phase, role in zip(phase_keys, perm):
                element = triad[phase].get("element", "[Missing]")
                weight = self.role_weights.get(role, 0)
                score += weight
                mapping[phase] = {"element": element, "weight": role}
                line.append(f"{phase.title()}={role}({element})")

            all_results.append({"mapping": mapping, "score": score})

            trace_lines.append(f"{' | '.join(line)} => Score: {score:.2f}")

            if score > best_score:
                best_score = score
                best_mapping = mapping

        trace_lines.append("")
        trace_lines.append(f"✅ Selected mapping: {self._mapping_summary(best_mapping)}")

        return {
            "best_mapping": best_mapping,
            "score": best_score,
            "permutations": all_results,
            "trace": "\n".join(trace_lines)
        }

    def _mapping_summary(self, mapping: Dict[str, Dict]) -> str:
        return " | ".join(
            f"{phase.title()}={info['weight']}({info['element']})"
            for phase, info in mapping.items()
        )
