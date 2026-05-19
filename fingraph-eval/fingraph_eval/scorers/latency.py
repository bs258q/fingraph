from typing import Any
from pydantic import BaseModel
from fingraph_eval.scorers.base import BaseScorer
from fingraph_eval.dataset import EvalCase


class LatencyScore(BaseModel):
    scorer: str = "latency"
    value: float = 1.0
    passed: bool = True
    tool_call_count: int = 0
    elapsed_seconds: float = 0.0
    notes: str = ""


class LatencyScorer(BaseScorer):
    name = "latency"

    def score(self, case: EvalCase, result: Any) -> LatencyScore:
        elapsed = getattr(result, "_elapsed", 0.0)
        tc_count = len(getattr(result, "tool_calls", []))
        passed = elapsed < 30.0 and tc_count <= 10
        return LatencyScore(
            tool_call_count=tc_count,
            elapsed_seconds=elapsed,
            passed=passed,
            notes=f"{tc_count} tool calls in {elapsed:.1f}s",
        )
