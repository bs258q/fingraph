import pytest
from unittest.mock import MagicMock
from fingraph_agents.agents.base import BaseAgent
from fingraph_agents.tools.graph_tools import GraphTools
from fingraph_agents.result import AgentResult


class TestAgent(BaseAgent):
    system_prompt = "You are a test agent."
    tool_names = ["find_entity"]


@pytest.fixture
def mock_tools():
    tools = MagicMock(spec=GraphTools)
    tools.schemas.return_value = [{"name": "find_entity", "description": "Find entity", "input_schema": {"type": "object"}}]
    tools.dispatch.return_value = []
    return tools


@pytest.fixture
def mock_client():
    return MagicMock()


@pytest.mark.asyncio
async def test_agent_end_turn(mock_tools, mock_client) -> None:
    mock_text = MagicMock()
    mock_text.type = "text"
    mock_text.text = "Entity not found in graph."
    mock_response = MagicMock()
    mock_response.stop_reason = "end_turn"
    mock_response.content = [mock_text]
    mock_client.messages.create.return_value = mock_response

    agent = TestAgent(mock_tools, client=mock_client)
    result = await agent.run("Who owns Acme?")

    assert result.status == "COMPLETE"
    assert result.agent_name == "TestAgent"
    assert "Entity not found" in result.finding
    assert result.iterations == 1


@pytest.mark.asyncio
async def test_agent_tool_use_then_end_turn(mock_tools, mock_client) -> None:
    mock_tool_block = MagicMock()
    mock_tool_block.type = "tool_use"
    mock_tool_block.id = "tu-1"
    mock_tool_block.name = "find_entity"
    mock_tool_block.input = {"name": "Acme"}

    mock_resp1 = MagicMock()
    mock_resp1.stop_reason = "tool_use"
    mock_resp1.content = [mock_tool_block]

    mock_text = MagicMock()
    mock_text.type = "text"
    mock_text.text = "Found Acme Corp entity-001."
    mock_resp2 = MagicMock()
    mock_resp2.stop_reason = "end_turn"
    mock_resp2.content = [mock_text]

    mock_client.messages.create.side_effect = [mock_resp1, mock_resp2]
    mock_tools.dispatch.return_value = [{"entity_id": "entity-001", "caption": "Acme Corp"}]

    agent = TestAgent(mock_tools, client=mock_client)
    result = await agent.run("Who owns Acme?")

    assert result.status == "COMPLETE"
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].name == "find_entity"
    assert result.iterations == 2


@pytest.mark.asyncio
async def test_agent_max_iterations_timeout(mock_tools, mock_client) -> None:
    mock_tool_block = MagicMock()
    mock_tool_block.type = "tool_use"
    mock_tool_block.id = "tu-1"
    mock_tool_block.name = "find_entity"
    mock_tool_block.input = {"name": "X"}

    mock_text = MagicMock()
    mock_text.type = "text"
    mock_text.text = "Still searching..."

    mock_resp = MagicMock()
    mock_resp.stop_reason = "tool_use"
    mock_resp.content = [mock_tool_block]

    # Return a response with a text block on final iteration when extracting finding
    mock_resp_final = MagicMock()
    mock_resp_final.content = [mock_text]

    mock_client.messages.create.return_value = mock_resp

    agent = TestAgent(mock_tools, client=mock_client)
    agent.max_iterations = 2
    result = await agent.run("Loop forever")

    assert result.status == "TIMEOUT"
    assert result.error == "Max iterations reached"


@pytest.mark.asyncio
async def test_agent_claude_api_error(mock_tools, mock_client) -> None:
    mock_client.messages.create.side_effect = Exception("Rate limit exceeded")

    agent = TestAgent(mock_tools, client=mock_client)
    result = await agent.run("Query")

    assert result.status == "FAILED"
    assert "Rate limit exceeded" in result.error


def test_extract_finding(mock_tools) -> None:
    mock_text = MagicMock()
    mock_text.type = "text"
    mock_text.text = "The UBO is John Doe."
    mock_response = MagicMock()
    mock_response.content = [mock_text]

    agent = TestAgent(mock_tools)
    assert agent._extract_finding(mock_response) == "The UBO is John Doe."


def test_estimate_confidence_scales_with_length(mock_tools) -> None:
    agent = TestAgent(mock_tools)
    short = agent._estimate_confidence("Short.")
    long = agent._estimate_confidence("x" * 600)
    assert 0 <= short <= 1
    assert long > short
    assert long <= 0.95
