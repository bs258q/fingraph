import pytest
from unittest.mock import MagicMock, AsyncMock
from fingraph_eval.runner import EvalRunner, ReportData
from fingraph_eval.dataset import EvalCase, Dataset


@pytest.mark.asyncio
async def test_runner_produces_case_results() -> None:
    case = EvalCase(id="kyc-001", query="Who owns Shell Corp?", expected={"ubos": ["john doe"], "sanctioned": True}, agent_type="kyc")
    dataset = Dataset(cases=[case])

    mock_result = MagicMock()
    mock_result.finding = "John Doe is the UBO."
    mock_result.structured = {"ubos": ["john doe"]}
    mock_result.tool_calls = []

    mock_agent = MagicMock()
    mock_agent.run = AsyncMock(return_value=mock_result)

    runner = EvalRunner(agent=mock_agent, dataset=dataset, agent_type="kyc")
    report = await runner.run()

    assert len(report.case_results) == 1
    assert report.case_results[0].case_id == "kyc-001"
    assert report.aggregate["total"] == 1


@pytest.mark.asyncio
async def test_runner_aggregate_pass_rate() -> None:
    cases = [
        EvalCase(id="t1", query="Q1", expected={"ubos": ["alice"]}, agent_type="kyc"),
        EvalCase(id="t2", query="Q2", expected={"ubos": ["bob"]}, agent_type="kyc"),
    ]
    dataset = Dataset(cases=cases)

    def make_result(ubo):
        r = MagicMock()
        r.finding = f"{ubo} is the UBO."
        r.structured = {"ubos": [ubo]}
        r.tool_calls = []
        return r

    mock_agent = MagicMock()
    mock_agent.run = AsyncMock(side_effect=[make_result("alice"), make_result("bob")])

    runner = EvalRunner(agent=mock_agent, dataset=dataset, agent_type="kyc")
    report = await runner.run()

    assert report.aggregate["total"] == 2
    assert 0.0 <= report.aggregate["pass_rate"] <= 1.0
