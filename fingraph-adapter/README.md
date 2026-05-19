# fingraph-adapter

Thin bridge: loads OpenSanctions FtM bulk exports into Neo4j using native FtM schema. ~150 lines.

## Install

```bash
pip install fingraph-adapter
```

## Usage

### Python
```python
from fingraph_adapter import FtMLoader

loader = FtMLoader("bolt://localhost:7687", "neo4j", "password")
stats = loader.load("/path/to/opensanctions-default.ftm.json")
print(f"Created {stats['nodes_created']} nodes, {stats['edges_created']} edges")
loader.close()
```

### CLI
```bash
python -m fingraph_adapter /path/to/export.ftm.json --uri bolt://localhost:7687
```

## FtM Input Format

Newline-delimited JSON, each line:
```json
{"id": "entity-id", "schema": "LegalEntity", "properties": {"name": ["Acme Corp"]}, "datasets": ["us_ofac_sdn"]}
```

## Adjacency → Edges

| FtM property | Neo4j relationship |
|---|---|
| `ownerEntity` | `OWNS` |
| `asset` | `OWNS` (reversed) |
| `member` | `MEMBER_OF` |
| `sanctions` | `SANCTIONED_BY` |
| `addressEntity` | `LOCATED_AT` |

## License

Apache 2.0
