from neo4j import Session


class EdgeMapper:
    ADJACENCY_MAP = {
        "ownerEntity": ("OWNS", "source"),
        "asset": ("OWNS", "target"),
        "member": ("MEMBER_OF", "source"),
        "sanctions": ("SANCTIONED_BY", "source"),
        "addressEntity": ("LOCATED_AT", "source"),
    }

    def __init__(self, session: Session):
        self.session = session

    def create_edge(self, entity_id: str, prop: str, target_id: str) -> dict[str, int]:
        if prop not in self.ADJACENCY_MAP:
            return {"created": 0, "updated": 0}
        rel_type, direction = self.ADJACENCY_MAP[prop]
        if direction == "source":
            cypher = f"MATCH (source {{node_id: $source_id}}), (target {{node_id: $target_id}}) MERGE (source)-[r:{rel_type}]->(target) RETURN elementId(r) as rel_id"
        else:
            cypher = f"MATCH (source {{node_id: $source_id}}), (target {{node_id: $target_id}}) MERGE (target)-[r:{rel_type}]->(source) RETURN elementId(r) as rel_id"
        result = self.session.run(cypher, source_id=entity_id, target_id=target_id)
        summary = result.consume()
        return {"created": summary.counters.relationships_created, "updated": 0}

    def batch_create_edges(self, adjacencies: list[dict]) -> dict[str, int]:
        stats = {"created": 0, "updated": 0}
        for adj in adjacencies:
            r = self.create_edge(adj["entity_id"], adj["prop"], adj["target_id"])
            stats["created"] += r["created"]
        return stats
