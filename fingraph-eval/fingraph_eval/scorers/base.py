from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel
from fingraph_eval.dataset import EvalCase


class ScoreResult(BaseModel):
    scorer: str
    value: float
    passed: bool
    notes: str = ""


class BaseScorer(ABC):
    name: str = ""

    @abstractmethod
    def score(self, case: EvalCase, result: Any) -> ScoreResult: ...
