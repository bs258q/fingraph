import pytest
from unittest.mock import MagicMock
from fingraph_adapter.edges import EdgeMapper


@pytest.fixture
def mock_session():
    session = MagicMock()
    mock_result = MagicMock()
    mock_summary = MagicMock()
    mock_summary.counters.relationships_created = 1
    mock_result.consume.return_value = mock_summary
    session.run.return_value = mock_result
    return session


def test_create_owns_edge(mock_session) -> None:
    mapper = EdgeMapper(mock_session)
    result = mapper.create_edge("entity-001", "ownerEntity", "entity-002")
    assert result["created"] == 1
    cypher = mock_session.run.call_args[0][0]
    assert "OWNS" in cypher


def test_create_asset_edge_reverses_direction(mock_session) -> None:
    mapper = EdgeMapper(mock_session)
    mapper.create_edge("entity-001", "asset", "entity-002")
    cypher = mock_session.run.call_args[0][0]
    assert "target)-[r:OWNS]->(source)" in cypher


def test_create_member_edge(mock_session) -> None:
    mapper = EdgeMapper(mock_session)
    result = mapper.create_edge("p1", "member", "org1")
    assert result["created"] == 1
    assert "MEMBER_OF" in mock_session.run.call_args[0][0]


def test_create_sanction_edge(mock_session) -> None:
    mapper = EdgeMapper(mock_session)
    result = mapper.create_edge("p1", "sanctions", "sanction1")
    assert result["created"] == 1
    assert "SANCTIONED_BY" in mock_session.run.call_args[0][0]


def test_create_address_edge(mock_session) -> None:
    mapper = EdgeMapper(mock_session)
    result = mapper.create_edge("org1", "addressEntity", "addr1")
    assert result["created"] == 1
    assert "LOCATED_AT" in mock_session.run.call_args[0][0]


def test_unknown_property_ignored(mock_session) -> None:
    mapper = EdgeMapper(mock_session)
    result = mapper.create_edge("e1", "unknownProp", "e2")
    assert result["created"] == 0
    mock_session.run.assert_not_called()


def test_batch_create_edges(mock_session) -> None:
    mapper = EdgeMapper(mock_session)
    adjacencies = [
        {"entity_id": "e1", "prop": "ownerEntity", "target_id": "e2"},
        {"entity_id": "e2", "prop": "addressEntity", "target_id": "e3"},
        {"entity_id": "e3", "prop": "unknownProp", "target_id": "e1"},
    ]
    result = mapper.batch_create_edges(adjacencies)
    assert result["created"] == 2
    assert mock_session.run.call_count == 2


def test_create_edge_params(mock_session) -> None:
    mapper = EdgeMapper(mock_session)
    mapper.create_edge("src-123", "ownerEntity", "tgt-456")
    params = mock_session.run.call_args[1]
    assert params["source_id"] == "src-123"
    assert params["target_id"] == "tgt-456"
