import pytest
from unittest.mock import MagicMock
from fingraph_eval.scorers.ubo_accuracy import UBOAccuracyScorer
from fingraph_eval.scorers.sanctions_recall import SanctionsRecallScorer
from fingraph_eval.scorers.fraud_precision import FraudPrecisionScorer
from fingraph_eval.scorers.latency import LatencyScorer
from fingraph_eval.dataset import EvalCase


def make_case(expected: dict, agent_type: str = "kyc") -> EvalCase:
    return EvalCase(id="t1", query="Q", expected=expected, agent_type=agent_type)


def make_result(finding: str, structured: dict = None, tool_calls: list = None, elapsed: float = 1.0):
    r = MagicMock()
    r.finding = finding
    r.structured = structured or {}
    r.tool_calls = tool_calls or []
    r._elapsed = elapsed
    return r


def test_ubo_accuracy_correct() -> None:
    case = make_case({"ubos": ["John Doe"]})
    result = make_result("John Doe is the UBO.", {"ubos": ["John Doe"]})
    score = UBOAccuracyScorer().score(case, result)
    assert score.value == 1.0
    assert score.passed


def test_ubo_accuracy_wrong() -> None:
    case = make_case({"ubos": ["John Doe"]})
    result = make_result("Jane Smith is the UBO.", {"ubos": ["Jane Smith"]})
    score = UBOAccuracyScorer().score(case, result)
    assert score.value == 0.0
    assert not score.passed


def test_sanctions_recall_hit_detected() -> None:
    case = make_case({"sanctioned": True}, agent_type="sanctions")
    result = make_result("Shell Corp: HIT on OFAC.", {"hits": 1})
    score = SanctionsRecallScorer().score(case, result)
    assert score.value == 1.0
    assert score.passed


def test_sanctions_recall_miss_penalized() -> None:
    case = make_case({"sanctioned": True}, agent_type="sanctions")
    result = make_result("Entity is CLEAR.", {"hits": 0})
    score = SanctionsRecallScorer().score(case, result)
    assert score.value == 0.0
    assert not score.passed


def test_fraud_precision_correct() -> None:
    case = make_case({"fraud": True, "pattern": "shell_company"}, agent_type="fraud")
    result = make_result("Suspicious shell company indicators. ESCALATE.")
    score = FraudPrecisionScorer().score(case, result)
    assert score.value >= 0.5
    assert score.passed


def test_latency_scorer() -> None:
    case = make_case({})
    result = make_result("Done.", elapsed=2.5)
    result.tool_calls = [MagicMock(), MagicMock()]
    score = LatencyScorer().score(case, result)
    assert score.tool_call_count == 2
    assert score.elapsed_seconds == 2.5
    assert score.passed
