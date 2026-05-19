import json
import pytest
from unittest.mock import MagicMock, patch
from fingraph_adapter.loader import FtMLoader


@pytest.fixture
def mock_driver():
    driver = MagicMock()
    return driver


@pytest.fixture
def ftm_json_file(tmp_path):
    entities = [
        {"id": "entity-001", "schema": "LegalEntity", "properties": {"name": ["Acme Corp"], "country": ["us"]}, "datasets": ["us_ofac_sdn"]},
        {"id": "entity-002", "schema": "Person", "properties": {"name": ["John Doe"], "birthDate": ["1980-01-01"]}, "datasets": ["us_ofac_sdn"]},
        {"id": "entity-003", "schema": "Address", "properties": {"street": ["123 Main St"], "city": ["New York"]}, "datasets": ["global_sanctions"]},
    ]
    f = tmp_path / "export.ftm.json"
    f.write_text("\n".join(json.dumps(e) for e in entities) + "\n")
    return f


def _setup_mock_session(mock_driver, nodes_created=1):
    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_summary = MagicMock()
    mock_summary.counters.nodes_created = nodes_created
    mock_summary.counters.properties_set = 5
    mock_result.consume.return_value = mock_summary
    mock_session.run.return_value = mock_result
    mock_driver.session.return_value.__enter__ = lambda s: mock_session
    mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
    return mock_session


def test_loader_init(mock_driver) -> None:
    with patch("fingraph_adapter.loader.GraphDatabase.driver", return_value=mock_driver):
        loader = FtMLoader("bolt://localhost:7687", "neo4j", "password")
        assert loader.driver == mock_driver


def test_load_creates_nodes(mock_driver, ftm_json_file) -> None:
    mock_session = _setup_mock_session(mock_driver)
    with patch("fingraph_adapter.loader.GraphDatabase.driver", return_value=mock_driver):
        loader = FtMLoader("bolt://localhost:7687", "neo4j", "password")
        stats = loader.load(str(ftm_json_file))
    assert stats["nodes_created"] == 3
    assert mock_session.run.call_count == 3


def test_load_flattens_list_properties(mock_driver, ftm_json_file) -> None:
    mock_session = _setup_mock_session(mock_driver)
    with patch("fingraph_adapter.loader.GraphDatabase.driver", return_value=mock_driver):
        loader = FtMLoader("bolt://localhost:7687", "neo4j", "password")
        loader.load(str(ftm_json_file))
    first_call = mock_session.run.call_args_list[0]
    params = first_call[1]
    assert params["name"] == "Acme Corp"
    assert "LegalEntity" in first_call[0][0]


def test_load_invalid_json_raises_error(mock_driver, tmp_path) -> None:
    bad_file = tmp_path / "bad.ftm.json"
    bad_file.write_text('{"incomplete": ')
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__ = lambda s: mock_session
    mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
    with patch("fingraph_adapter.loader.GraphDatabase.driver", return_value=mock_driver):
        loader = FtMLoader("bolt://localhost:7687", "neo4j", "password")
        with pytest.raises(ValueError, match="Invalid JSON"):
            loader.load(str(bad_file))


def test_load_returns_stats(mock_driver, ftm_json_file) -> None:
    _setup_mock_session(mock_driver)
    with patch("fingraph_adapter.loader.GraphDatabase.driver", return_value=mock_driver):
        loader = FtMLoader("bolt://localhost:7687", "neo4j", "password")
        stats = loader.load(str(ftm_json_file))
    assert "nodes_created" in stats
    assert "nodes_updated" in stats
    assert "edges_created" in stats
    assert stats["nodes_created"] == 3


def test_loader_close(mock_driver) -> None:
    with patch("fingraph_adapter.loader.GraphDatabase.driver", return_value=mock_driver):
        loader = FtMLoader("bolt://localhost:7687", "neo4j", "password")
        loader.close()
        mock_driver.close.assert_called_once()
