import json
from pydantic import BaseModel
from typing import Any


class EvalCase(BaseModel):
    id: str
    query: str
    expected: dict[str, Any]
    agent_type: str  # kyc|sanctions|fraud|aml|pep|adverse_media|counterparty|contagion|filing
    tags: list[str] = []
    notes: str = ""


class Dataset(BaseModel):
    cases: list[EvalCase]

    @classmethod
    def from_json(cls, path: str) -> "Dataset":
        with open(path) as f:
            raw = json.load(f)
        return cls(cases=[EvalCase(**c) for c in raw])

    def filter(self, agent_type: str | None = None, tags: list[str] | None = None) -> "Dataset":
        cases = self.cases
        if agent_type:
            cases = [c for c in cases if c.agent_type == agent_type]
        if tags:
            cases = [c for c in cases if all(t in c.tags for t in tags)]
        return Dataset(cases=cases)
