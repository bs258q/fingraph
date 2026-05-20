# fingraph

Open-source LLM agent layer + eval harness for financial compliance graphs.

Built on [OpenSanctions](https://opensanctions.org) and [follow-the-money (FtM)](https://followthemoney.tech) — not competing with them, extending them.

## The Gap

RegTech startups already have compliance graphs. What's missing:
- LLM agents that traverse those graphs to answer KYC/AML/fraud questions
- An eval harness to validate agent accuracy before production deployment

fingraph fills both gaps.

## Packages

| Package | What it does | Install |
|---|---|---|
| `fingraph-adapter` | Loads OpenSanctions FtM exports → Neo4j | `pip install fingraph-adapter` |
| `fingraph-agents` | 9 Claude agents for KYC, AML, sanctions, fraud | `pip install fingraph-agents` |
| `fingraph-eval` | Eval harness — measure agent accuracy, CI-ready | `pip install fingraph-eval` |

## Quickstart (5 minutes)

```bash
# 1. Start Neo4j
docker-compose up -d

# 2. Load OpenSanctions data
pip install fingraph-adapter
python -m fingraph_adapter opensanctions-default.ftm.json

# 3. Query with an agent
pip install fingraph-agents
python -c "
import asyncio
from neo4j import GraphDatabase
from fingraph_agents import KYCAgent, GraphTools

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'fingraph_dev'))
with driver.session() as session:
    agent = KYCAgent(tools=GraphTools(session))
    result = asyncio.run(agent.run('Who are the beneficial owners of Acme Corp?'))
    print(result.finding)
driver.close()
"
```

## Agents

| Agent | Question | Max Tool Calls |
|---|---|---|
| `KYCAgent` | Who are the UBOs? Any sanctions in chain? | 6 |
| `SanctionsScreeningAgent` | Is this entity on a sanctions list? | 2 per entity |
| `FraudSignalAgent` | Shell company / fraud indicators? | 4 |
| `AMLTypologyAgent` | Matches laundering typologies? | 3 |
| `CounterpartyRiskAgent` | Full exposure to this entity? | 7 |
| `PEPDetectionAgent` | Is this person politically exposed? | 3 |
| `AdverseMediaAgent` | Negative news on this entity? | 4 |
| `NetworkContagionAgent` | If this entity fails, who's exposed? | 6 |
| `RegulatoryFilingAgent` | Disclosure gaps / hidden connections? | 3 |

Each agent has explicit tool call caps in its system prompt to prevent redundant graph lookups and keep latency under 45 seconds. The eval harness enforces this — latency scorer fails any run exceeding the threshold.

## Eval Harness

```python
from fingraph_eval import Dataset, EvalRunner, Reporter

dataset = Dataset.from_json("datasets/synthetic/kyc_cases.json")
runner = EvalRunner(agent=agent, dataset=dataset, agent_type="kyc")
report = asyncio.run(runner.run())
Reporter(report).save_html("report.html")
print(f"Pass rate: {report.aggregate['pass_rate']:.0%}")
```

CI integration: `assert report.aggregate["pass_rate"] >= 0.8`

## Architecture

```
OpenSanctions FtM export
        ↓
fingraph-adapter (FtM → Neo4j)
        ↓
Neo4j 5.x (FtM-schema graph)
        ↓
fingraph-agents (Claude tool-use loop)
  ├── 8 graph tools (Cypher queries)
  └── 9 compliance agents
        ↓
AgentResult (finding + evidence + tool audit trail)
        ↓
fingraph-eval (accuracy scoring + HTML reports)
```

## Requirements

- Python 3.10+
- Neo4j 5.x (free community edition works)
- `ANTHROPIC_API_KEY`

## Local Dev

```bash
docker-compose up -d   # Neo4j at localhost:7687
pip install -e fingraph-adapter/.[dev]
pip install -e fingraph-agents/.[dev]
pip install -e fingraph-eval/.[dev]
pytest fingraph-adapter/fingraph_adapter/tests/ fingraph-agents/fingraph_agents/tests/ fingraph-eval/fingraph_eval/tests/
```

## Roadmap

### v0.1 (current)
- fingraph-adapter — FtM→Neo4j bridge
- fingraph-agents — 9 compliance agents
- fingraph-eval — accuracy eval harness

### v0.2 — fingraph-payments
Intent-based payment verification agent:
- Intercepts payment intents (Stripe/Moov webhook)
- Cross-references payee against compliance graph (UBO chain, sanctions, fraud signals)
- Returns: AUTHORIZE / HOLD / BLOCK + explainable reasoning + audit trail
- fingraph becomes the compliance substrate for payment decisioning

Target: fintechs, neobanks, payment processors who need explainable compliance decisions at payment time.

## License

Apache 2.0

## Contributing

Issues and PRs welcome. See `datasets/README.md` for contributing eval cases.
