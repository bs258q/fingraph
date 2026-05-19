from typing import Any
from fingraph_eval.scorers.base import BaseScorer, ScoreResult
from fingraph_eval.dataset import EvalCase


class UBOAccuracyScorer(BaseScorer):
    name = "ubo_accuracy"

    def score(self, case: EvalCase, result: Any) -> ScoreResult:
        expected = {u.lower() for u in case.expected.get("ubos", [])}
        if not expected:
            return ScoreResult(scorer=self.name, value=1.0, passed=True, notes="No UBOs to check")

        # Try structured first, fall back to text search
        found_raw = result.structured.get("ubos", []) if hasattr(result, "structured") else []
        if isinstance(found_raw, list) and found_raw:
            found = {u.lower() for u in found_raw}
        else:
            finding = result.finding if hasattr(result, "finding") else str(result)
            found = {u for u in expected if u in finding.lower()}

        if not found:
            return ScoreResult(scorer=self.name, value=0.0, passed=False, notes=f"No UBOs found. Expected: {expected}")

        intersection = expected & found
        precision = len(intersection) / len(found)
        recall = len(intersection) / len(expected)
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        return ScoreResult(scorer=self.name, value=f1, passed=f1 >= 0.8, notes=f"F1={f1:.2f} expected={expected} found={found}")
