from typing import Any
from fingraph_eval.scorers.base import BaseScorer, ScoreResult
from fingraph_eval.dataset import EvalCase


class FraudPrecisionScorer(BaseScorer):
    name = "fraud_precision"

    def score(self, case: EvalCase, result: Any) -> ScoreResult:
        expected_fraud = case.expected.get("fraud", False)
        finding = result.finding if hasattr(result, "finding") else str(result)
        found_fraud = any(w in finding.upper() for w in ("ESCALATE", "REVIEW", "SUSPICIOUS"))
        if expected_fraud and found_fraud:
            expected_pattern = case.expected.get("pattern", "")
            matched = not expected_pattern or expected_pattern in finding.lower()
            v = 1.0 if matched else 0.7
            return ScoreResult(scorer=self.name, value=v, passed=True, notes="Correct fraud detection")
        if not expected_fraud and found_fraud:
            return ScoreResult(scorer=self.name, value=0.0, passed=False, notes="False positive")
        if expected_fraud and not found_fraud:
            return ScoreResult(scorer=self.name, value=0.2, passed=False, notes="False negative: missed fraud")
        return ScoreResult(scorer=self.name, value=1.0, passed=True, notes="Correct: clean")
