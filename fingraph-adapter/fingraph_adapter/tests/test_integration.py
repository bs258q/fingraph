import json
import pytest
from unittest.mock import MagicMock, patch
from fingraph_adapter.loader import FtMLoader


@pytest.fixture
def mock_driver():
    return MagicMock()


@pytest.fixture
def ftm_integration_file(tmp_path):
    entities = [
        {"id": "entity-001", "schema": "LegalEntity", "properties": {"name": ["Acme Corp"], "country": ["us"]}, "datasets": ["us_ofac_sdn"]},
        {"id": "entity-002", "schema": "LegalEntity", "properties": {"name": ["Omega Inc"], "country": ["ch"]}, "datasets": ["us_ofac_sdn"]},
        {"id": "entity-003", "schema": "Person", "properties": {"name": ["Jane Smith"], "ownerEntity": ["entity-001"]}, "datasets": ["us_ofac_sdn"]},
        {"id": "entity-004", "schema": "Sanction", "properties": {"name": ["OFAC SDN Listing"]}, "datasets": ["us_ofac_sdn"]},
        {"id": "entity-005", "schema": "Person", "properties": {"name": ["John Doe"], "sanctions": ["entity-004"]}, "datasets": ["us_ofac_sdn"]},
    ]
    f = tmp_path / "integration.ftm.json"
    f.write_text("\n".join(json.dumps(e) for e in entities) + "\n")
    return f


def _setup_mock(mock_driver, nodes_created=1, rels_created=1):
    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_summary = MagicMock()
    mock_summary.counters.nodes_created = nodes_created
    mock_summary.counters.properties_set = 5
    mock_summary.counters.relationships_created = rels_created
    mock_result.consume.return_value = mock_summary
    mock_session.run.return_value = mock_result
    mock_driver.session.return_value.__enter__ = lambda s: mock_session
    mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
    return mock_session


def test_end_to_end_load_with_edges(mock_driver, ftm_integration_file) -> None:
    _setup_mock(mock_driver)
    with patch("fingraph_adapter.loader.GraphDatabase.driver", return_value=mock_driver):
        loader = FtMLoader("bolt://localhost:7687", "neo4j", "password")
        stats = loader.load(str(ftm_integration_file))
    assert stats["nodes_created"] == 5
    assert stats["edges_created"] >= 2


def test_integration_session_run_called_for_all_entities(mock_driver, ftm_integration_file) -> None:
    mock_session = _setup_mock(mock_driver)
    with patch("fingraph_adapter.loader.GraphDatabase.driver", return_value=mock_driver):
        loader = FtMLoader("bolt://localhost:7687", "neo4j", "password")
        loader.load(str(ftm_integration_file))
    assert mock_session.run.call_count >= 5
