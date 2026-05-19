import json
import pytest
from fingraph_eval.report import Reporter
from fingraph_eval.runner import ReportData, EvalCaseResult


def make_report() -> ReportData:
    return ReportData(
        agent_type="kyc",
        case_results=[EvalCaseResult(
            case_id="kyc-001", query="Who owns Acme?",
            finding="John Doe is the UBO.",
            scores=[{"scorer": "ubo_accuracy", "value": 1.0, "passed": True, "notes": ""}],
            passed=True, elapsed_seconds=1.5,
        )],
        aggregate={"total": 1, "passed": 1, "failed": 0, "pass_rate": 1.0, "avg_elapsed_seconds": 1.5},
    )


def test_reporter_saves_json(tmp_path) -> None:
    out = tmp_path / "report.json"
    Reporter(make_report()).save_json(str(out))
    data = json.loads(out.read_text())
    assert data["aggregate"]["total"] == 1
    assert data["case_results"][0]["case_id"] == "kyc-001"


def test_reporter_saves_html(tmp_path) -> None:
    out = tmp_path / "report.html"
    Reporter(make_report()).save_html(str(out))
    content = out.read_text()
    assert "kyc-001" in content
    assert "PASS" in content
