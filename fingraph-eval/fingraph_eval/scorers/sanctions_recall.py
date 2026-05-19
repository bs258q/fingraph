from typing import Any
from fingraph_eval.scorers.base import BaseScorer, ScoreResult
from fingraph_eval.dataset import EvalCase


class SanctionsRecallScorer(BaseScorer):
    name = "sanctions_recall"

    def score(self, case: EvalCase, result: Any) -> ScoreResult:
        expected_hit = case.expected.get("sanctioned", False)
        finding = result.finding if hasattr(result, "finding") else str(result)
        found_hit = (
            "hit" in finding.lower()
            or (hasattr(result, "structured") and result.structured.get("hits", 0) > 0)
        )
        if expected_hit and not found_hit:
            return ScoreResult(scorer=self.name, value=0.0, passed=False, notes="FALSE NEGATIVE: missed sanctions hit")
        if not expected_hit and found_hit:
            return ScoreResult(scorer=self.name, value=0.5, passed=False, notes="False positive: clean entity flagged")
        return ScoreResult(scorer=self.name, value=1.0, passed=True, notes="Correct")
