import pytest
from unittest.mock import MagicMock
from fingraph_agents.tools.graph_tools import GraphTools


@pytest.fixture
def mock_session():
    return MagicMock()


def _mock_run(session, records):
    session.run.return_value = iter(records)


def test_graph_tools_init(mock_session) -> None:
    tools = GraphTools(mock_session)
    assert tools.session == mock_session


def test_find_entity(mock_session) -> None:
    rec = MagicMock()
    rec.__getitem__ = lambda s, k: {"entity_id": "e-001", "caption": "Acme Corp", "schema": "LegalEntity"}[k]
    mock_session.run.return_value = [rec]
    tools = GraphTools(mock_session)
    results = tools.find_entity("Acme")
    assert len(results) == 1
    assert results[0]["caption"] == "Acme Corp"


def test_check_sanctions_returns_list(mock_session) -> None:
    rec = MagicMock()
    rec.__getitem__ = lambda s, k: {"entity_id": "e-001", "caption": "John", "sanction_id": "s-001", "dataset": "us_ofac_sdn"}[k]
    mock_session.run.return_value = [rec]
    tools = GraphTools(mock_session)
    results = tools.check_sanctions("e-001")
    assert len(results) == 1
    assert results[0]["dataset"] == "us_ofac_sdn"


def test_score_jurisdiction_high_risk(mock_session) -> None:
    tools = GraphTools(mock_session)
    result = tools.score_jurisdiction("kp")
    assert result["risk_level"] == "HIGH"
    assert result["risk_score"] >= 70


def test_score_jurisdiction_low_risk(mock_session) -> None:
    tools = GraphTools(mock_session)
    result = tools.score_jurisdiction("us")
    assert result["risk_level"] == "LOW"


def test_dispatch_valid_tool(mock_session) -> None:
    mock_session.run.return_value = []
    tools = GraphTools(mock_session)
    result = tools.dispatch("find_entity", {"name": "Acme"})
    assert isinstance(result, list)


def test_dispatch_invalid_tool(mock_session) -> None:
    tools = GraphTools(mock_session)
    with pytest.raises(ValueError, match="Unknown tool"):
        tools.dispatch("bad_tool", {})


def test_schemas_returns_8_tools(mock_session) -> None:
    tools = GraphTools(mock_session)
    schemas = tools.schemas()
    assert len(schemas) == 8
    names = [s["name"] for s in schemas]
    assert "find_entity" in names
    assert "check_sanctions" in names
    assert "score_jurisdiction" in names


def test_get_relationships_returns_list(mock_session) -> None:
    rec = MagicMock()
    rec.__getitem__ = lambda s, k: {"source_id": "e-001", "source_caption": "Acme", "rel_type": "OWNS", "target_id": "e-002", "target_caption": "Sub Inc"}[k]
    mock_session.run.return_value = [rec]
    tools = GraphTools(mock_session)
    results = tools.get_relationships("e-001")
    assert len(results) == 1
    assert results[0]["rel_type"] == "OWNS"
