import pytest
from unittest.mock import MagicMock
from fingraph_agents.agents.fraud_signal import FraudSignalAgent
from fingraph_agents.agents.counterparty_risk import CounterpartyRiskAgent
from fingraph_agents.agents.pep_detection import PEPDetectionAgent
from fingraph_agents.agents.adverse_media import AdverseMediaAgent
from fingraph_agents.agents.network_contagion import NetworkContagionAgent
from fingraph_agents.agents.regulatory_filing import RegulatoryFilingAgent
from fingraph_agents.agents.aml_typology import AMLTypologyAgent
from fingraph_agents.tools.graph_tools import GraphTools


def make_mock_tools():
    tools = MagicMock(spec=GraphTools)
    tools.schemas.return_value = []
    tools.dispatch.return_value = []
    tools.session = MagicMock()
    tools.session.run.return_value = []
    return tools


def make_mock_client(text="Analysis complete. Risk: MEDIUM."):
    client = MagicMock()
    mock_text = MagicMock()
    mock_text.type = "text"
    mock_text.text = text
    mock_resp = MagicMock()
    mock_resp.stop_reason = "end_turn"
    mock_resp.content = [mock_text]
    client.messages.create.return_value = mock_resp
    return client


@pytest.mark.asyncio
async def test_fraud_signal_agent() -> None:
    agent = FraudSignalAgent(make_mock_tools(), client=make_mock_client("Risk score: 75/100. Action: ESCALATE."))
    result = await agent.run("Analyze Shell Corp for fraud indicators")
    assert result.status == "COMPLETE"
    assert result.agent_name == "FraudSignalAgent"


@pytest.mark.asyncio
async def test_counterparty_risk_agent() -> None:
    agent = CounterpartyRiskAgent(make_mock_tools(), client=make_mock_client("Overall rating: HIGH."))
    result = await agent.run("What is our exposure to Omega Inc?")
    assert result.status == "COMPLETE"
    assert result.agent_name == "CounterpartyRiskAgent"


@pytest.mark.asyncio
async def test_pep_detection_agent() -> None:
    agent = PEPDetectionAgent(make_mock_tools(), client=make_mock_client("PEP status: YES. Category: government official."))
    result = await agent.run("Is Jane Smith a PEP?")
    assert result.status == "COMPLETE"
    assert result.agent_name == "PEPDetectionAgent"


@pytest.mark.asyncio
async def test_adverse_media_agent() -> None:
    agent = AdverseMediaAgent(make_mock_tools(), client=make_mock_client("Severity: HIGH. Found fraud-related articles."))
    result = await agent.run("Any adverse media on Acme Corp?")
    assert result.status == "COMPLETE"
    assert result.agent_name == "AdverseMediaAgent"


@pytest.mark.asyncio
async def test_network_contagion_agent() -> None:
    agent = NetworkContagionAgent(make_mock_tools(), client=make_mock_client("Contagion risk: SYSTEMIC. 50 direct exposures."))
    result = await agent.run("If Global Bank fails, who is exposed?")
    assert result.status == "COMPLETE"
    assert result.agent_name == "NetworkContagionAgent"


@pytest.mark.asyncio
async def test_regulatory_filing_agent() -> None:
    agent = RegulatoryFilingAgent(make_mock_tools(), client=make_mock_client("Compliance risk: MATERIAL_ISSUES. 3 hidden connections found."))
    result = await agent.run("Review filings for Acme Corp")
    assert result.status == "COMPLETE"
    assert result.agent_name == "RegulatoryFilingAgent"


@pytest.mark.asyncio
async def test_aml_typology_agent() -> None:
    agent = AMLTypologyAgent(make_mock_tools(), client=make_mock_client("Matched typology: round_tripping. Confidence: 0.9. Escalation: URGENT."))
    result = await agent.run("Does Shell Corp match AML typologies?")
    assert result.status == "COMPLETE"
    assert result.agent_name == "AMLTypologyAgent"


def test_fraud_signal_parse_structured() -> None:
    agent = FraudSignalAgent(make_mock_tools())
    structured = agent._parse_structured("Risk score: 82/100. Recommended action: ESCALATE.")
    assert structured["risk_score"] == 82
    assert structured["action"] == "ESCALATE"


def test_adverse_media_parse_structured() -> None:
    agent = AdverseMediaAgent(make_mock_tools())
    structured = agent._parse_structured("Multiple articles found. Severity: HIGH.")
    assert structured["severity"] == "HIGH"
