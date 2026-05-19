# fingraph-agents

9 Claude API agents for KYC, AML, sanctions screening, fraud detection, and counterparty risk. Built for FtM-schema Neo4j graphs (OpenSanctions-native).

## Install

```bash
pip install fingraph-agents
```

Requires `ANTHROPIC_API_KEY` env var and a running Neo4j 5.x instance loaded with FtM data (use `fingraph-adapter`).

## Quickstart

```python
import asyncio
from neo4j import GraphDatabase
from fingraph_agents import KYCAgent, GraphTools

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
with driver.session() as session:
    tools = GraphTools(session)
    agent = KYCAgent(tools=tools)
    result = asyncio.run(agent.run("Who are the beneficial owners of Acme Corp?"))

print(result.finding)
print(f"Status: {result.status}, Confidence: {result.confidence:.0%}")
driver.close()
```

## Agents

| Agent | Question it answers |
|---|---|
| `KYCAgent` | Who are the UBOs? Any sanctions in ownership chain? |
| `SanctionsScreeningAgent` | Is this entity on a sanctions list? (bulk) |
| `FraudSignalAgent` | Does this entity show fraud/shell company indicators? |
| `AMLTypologyAgent` | Does this match known laundering typologies? |
| `CounterpartyRiskAgent` | What's our full exposure to this entity? |
| `PEPDetectionAgent` | Is this person politically exposed? |
| `AdverseMediaAgent` | Any negative news on this entity? |
| `NetworkContagionAgent` | If this entity fails, who's exposed? |
| `RegulatoryFilingAgent` | Any disclosure gaps or hidden connections? |

## FtM Compatibility

Works with any Neo4j graph loaded from OpenSanctions FtM format. Use `fingraph-adapter` to load:

```bash
pip install fingraph-adapter
python -m fingraph_adapter /path/to/opensanctions-default.ftm.json
```

## Architecture

```
Query → Agent (Claude tool-use loop) → GraphTools (8 Cypher tools) → Neo4j (FtM graph)
                                              ↓
                                        AgentResult
                                    (finding + tool calls + confidence)
```

## License

Apache 2.0
