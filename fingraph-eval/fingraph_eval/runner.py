import time
from typing import Any
from pydantic import BaseModel
from fingraph_eval.dataset import Dataset, EvalCase
from fingraph_eval.scorers.ubo_accuracy import UBOAccuracyScorer
from fingraph_eval.scorers.sanctions_recall import SanctionsRecallScorer
from fingraph_eval.scorers.fraud_precision import FraudPrecisionScorer
from fingraph_eval.scorers.latency import LatencyScorer

SCORER_MAP = {
    "kyc": [UBOAccuracyScorer(), LatencyScorer()],
    "sanctions": [SanctionsRecallScorer(), LatencyScorer()],
    "fraud": [FraudPrecisionScorer(), LatencyScorer()],
}


class EvalCaseResult(BaseModel):
    case_id: str
    query: str
    finding: str
    scores: list[dict]
    passed: bool
    elapsed_seconds: float


class ReportData(BaseModel):
    agent_type: str
    case_results: list[EvalCaseResult]
    aggregate: dict[str, Any]


class EvalRunner:
    def __init__(self, agent: Any, dataset: Dataset, agent_type: str):
        self._agent = agent
        self._dataset = dataset
        self._agent_type = agent_type
        self._scorers = SCORER_MAP.get(agent_type, [LatencyScorer()])

    async def run(self) -> ReportData:
        case_results: list[EvalCaseResult] = []
        for case in self._dataset.cases:
            start = time.monotonic()
            result = await self._agent.run(case.query)
            elapsed = time.monotonic() - start
            result._elapsed = elapsed

            scores = [s.score(case, result) for s in self._scorers]
            passed = all(s.passed for s in scores)
            case_results.append(EvalCaseResult(
                case_id=case.id,
                query=case.query,
                finding=getattr(result, "finding", str(result)),
                scores=[s.model_dump() for s in scores],
                passed=passed,
                elapsed_seconds=elapsed,
            ))

        total = len(case_results)
        passed_count = sum(1 for r in case_results if r.passed)
        avg_elapsed = sum(r.elapsed_seconds for r in case_results) / total if total else 0.0
        return ReportData(
            agent_type=self._agent_type,
            case_results=case_results,
            aggregate={
                "total": total,
                "passed": passed_count,
                "failed": total - passed_count,
                "pass_rate": passed_count / total if total else 0.0,
                "avg_elapsed_seconds": avg_elapsed,
            },
        )
