# fingraph-eval

Eval harness for fingraph agents. Measure accuracy of KYC, sanctions, fraud agents against ground-truth datasets before production deployment.

## Install

```bash
pip install fingraph-eval
```

## Usage

```python
import asyncio
from neo4j import GraphDatabase
from fingraph_agents import KYCAgent, GraphTools
from fingraph_eval import Dataset, EvalRunner, Reporter

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
with driver.session() as session:
    tools = GraphTools(session)
    agent = KYCAgent(tools=tools)
    dataset = Dataset.from_json("datasets/synthetic/kyc_cases.json")
    runner = EvalRunner(agent=agent, dataset=dataset, agent_type="kyc")
    report_data = asyncio.run(runner.run())

Reporter(report_data).save_html("kyc_report.html")
print(f"Pass rate: {report_data.aggregate['pass_rate']:.0%}")
driver.close()
```

## Scorers

| Agent | Scorer | Key Metric |
|---|---|---|
| KYC | `UBOAccuracyScorer` | F1 on UBO identification |
| Sanctions | `SanctionsRecallScorer` | Recall (false negatives = 0 score) |
| Fraud | `FraudPrecisionScorer` | Precision (FP cost analyst time) |
| All | `LatencyScorer` | Tool calls + elapsed seconds |

## CI Integration

```python
assert report_data.aggregate["pass_rate"] >= 0.8, "Agent accuracy below threshold"
```

## Contributing Eval Cases

See `datasets/README.md`.

## License

Apache 2.0
