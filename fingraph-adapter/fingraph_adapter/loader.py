import json
from typing import Any
from neo4j import GraphDatabase, Session, Driver


class FtMLoader:
    def __init__(self, uri: str, username: str, password: str):
        self.driver: Driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self) -> None:
        self.driver.close()

    def load(self, path: str) -> dict[str, int]:
        stats = {"nodes_created": 0, "nodes_updated": 0, "edges_created": 0}
        adjacencies: list[dict] = []

        with self.driver.session() as session:
            with open(path) as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    try:
                        entity = json.loads(line)
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Invalid JSON on line {line_num}: {e}")

                    r = self._upsert_entity(session, entity)
                    stats["nodes_created"] += r["created"]
                    stats["nodes_updated"] += r["updated"]

                    entity_id = entity.get("id", "")
                    for prop, values in entity.get("properties", {}).items():
                        if isinstance(values, list):
                            for val in values:
                                if isinstance(val, str) and val.startswith("entity-"):
                                    adjacencies.append({"entity_id": entity_id, "prop": prop, "target_id": val})

            if adjacencies:
                from .edges import EdgeMapper
                with self.driver.session() as session2:
                    mapper = EdgeMapper(session2)
                    r2 = mapper.batch_create_edges(adjacencies)
                    stats["edges_created"] = r2["created"]

        return stats

    def _upsert_entity(self, session: Session, entity: dict[str, Any]) -> dict[str, int]:
        entity_id = entity.get("id", "")
        schema = entity.get("schema", "Unknown")
        properties = entity.get("properties", {})
        datasets = entity.get("datasets", [])

        flat_props: dict[str, Any] = {}
        for key, values in properties.items():
            if isinstance(values, list):
                flat_props[key] = values[0] if values else None
            else:
                flat_props[key] = values

        caption = flat_props.get("name") or "Unknown"
        dataset = datasets[0] if datasets else "unknown"

        prop_sets = ", ".join(f"n.{k.replace('-','_')} = ${k}" for k in flat_props)
        set_clause = f", {prop_sets}" if prop_sets else ""

        cypher = f"""
        MERGE (n:{schema} {{node_id: $entity_id}})
        SET n.caption = $caption, n.schema = $schema, n.dataset = $dataset, n.id = $entity_id{set_clause}
        RETURN elementId(n) as elem_id
        """

        result = session.run(cypher, entity_id=entity_id, caption=caption, schema=schema, dataset=dataset, **flat_props)
        summary = result.consume()
        created = summary.counters.nodes_created
        updated = int(summary.counters.properties_set > 0 and created == 0)
        return {"created": created, "updated": updated}
