import pytest
from unittest.mock import MagicMock
from fingraph_agents.agents.sanctions_screening import SanctionsScreeningAgent
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
    mock_text.text = "Shell Corp: HIT on us_ofac_sdn (confidence: 0.95). Acme Corp: CLEAR."
    mock_resp = MagicMock()
    mock_resp.stop_reason = "end_turn"
    mock_resp.content = [mock_text]
    client.messages.create.return_value = mock_resp
    return client


@pytest.mark.asyncio
async def test_sanctions_agent_returns_result(mock_tools, mock_client) -> None:
    agent = SanctionsScreeningAgent(mock_tools, client=mock_client)
    result = await agent.run("Screen: Shell Corp, Acme Corp")
    assert result.status == "COMPLETE"
    assert result.agent_name == "SanctionsScreeningAgent"


@pytest.mark.asyncio
async def test_sanctions_agent_parse_structured(mock_tools, mock_client) -> None:
    agent = SanctionsScreeningAgent(mock_tools, client=mock_client)
    structured = agent._parse_structured("Shell Corp: HIT. Acme Corp: CLEAR. Omega Ltd: CLEAR.")
    assert structured["hits"] >= 1
    assert structured["clears"] >= 2


def test_sanctions_agent_tool_names(mock_tools) -> None:
    agent = SanctionsScreeningAgent(mock_tools)
    assert "find_entity" in agent.tool_names
    assert "check_sanctions" in agent.tool_names
