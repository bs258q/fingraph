import json
import pytest
from fingraph_eval.dataset import EvalCase, Dataset


def test_evalcase_fields() -> None:
    case = EvalCase(id="kyc-001", query="Who owns Acme?", expected={"ubos": ["John"]}, agent_type="kyc")
    assert case.id == "kyc-001"
    assert case.agent_type == "kyc"


def test_dataset_from_json(tmp_path) -> None:
    f = tmp_path / "cases.json"
    f.write_text(json.dumps([{"id": "t1", "query": "Q", "expected": {}, "agent_type": "kyc", "tags": []}]))
    ds = Dataset.from_json(str(f))
    assert len(ds.cases) == 1
    assert ds.cases[0].id == "t1"


def test_dataset_filter_by_agent_type(tmp_path) -> None:
    f = tmp_path / "cases.json"
    f.write_text(json.dumps([
        {"id": "k1", "query": "Q", "expected": {}, "agent_type": "kyc", "tags": []},
        {"id": "s1", "query": "Q", "expected": {}, "agent_type": "sanctions", "tags": []},
    ]))
    ds = Dataset.from_json(str(f))
    kyc = ds.filter(agent_type="kyc")
    assert len(kyc.cases) == 1
    assert kyc.cases[0].id == "k1"
