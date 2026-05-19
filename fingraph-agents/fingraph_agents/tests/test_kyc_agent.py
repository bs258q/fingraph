import pytest
from unittest.mock import MagicMock
from fingraph_agents.agents.kyc import KYCAgent
from fingraph_agents.tools.graph_tools import GraphTools


@pytest.fixture
def mock_tools():
    tools = MagicMock(spec=GraphTools)
    tools.schemas.return_value = []
    tools.dispatch.return_value = []
    return tools


@pytest.fixture
def mock_client():
    client = MagicMock()
    mock_text = MagicMock()
    mock_text.type = "text"
    mock_text.text = "John Doe is the UBO of Acme Corp with 51% ownership. Risk: HIGH — Shell Corp is SANCTIONED by OFAC."
    mock_resp = MagicMock()
    mock_resp.stop_reason = "end_turn"
    mock_resp.content = [mock_text]
    client.messages.create.return_value = mock_resp
    return client


@pytest.mark.asyncio
async def test_kyc_agent_returns_result(mock_tools, mock_client) -> None:
    agent = KYCAgent(mock_tools, client=mock_client)
    result = await agent.run("Who are the beneficial owners of Acme Corp?")
    assert result.status == "COMPLETE"
    assert result.agent_name == "KYCAgent"
    assert len(result.finding) > 0


@pytest.mark.asyncio
async def test_kyc_agent_parse_structured_high_risk(mock_tools, mock_client) -> None:
    agent = KYCAgent(mock_tools, client=mock_client)
    structured = agent._parse_structured("Overall risk: HIGH. UBO is John Doe.")
    assert structured["risk_level"] == "HIGH"


@pytest.mark.asyncio
async def test_kyc_agent_parse_structured_low_risk(mock_tools, mock_client) -> None:
    agent = KYCAgent(mock_tools, client=mock_client)
    structured = agent._parse_structured("No sanctions found. Risk: LOW.")
    assert structured["risk_level"] == "LOW"


def test_kyc_agent_tool_names(mock_tools) -> None:
    agent = KYCAgent(mock_tools)
    assert "find_entity" in agent.tool_names
    assert "traverse_ownership" in agent.tool_names
    assert "check_sanctions" in agent.tool_names
    assert "score_jurisdiction" in agent.tool_names
