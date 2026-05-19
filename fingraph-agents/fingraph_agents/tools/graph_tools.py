from typing import Any
from neo4j import Session


class GraphTools:
    def __init__(self, session: Session):
        self.session = session

    def find_entity(self, name: str, limit: int = 5) -> list[dict]:
        result = self.session.run(
            "MATCH (n) WHERE toLower(n.caption) CONTAINS toLower($name) "
            "RETURN n.id as entity_id, n.caption as caption, n.schema as schema LIMIT $limit",
            name=name, limit=limit,
        )
        return [{"entity_id": r["entity_id"], "caption": r["caption"], "schema": r["schema"]} for r in result]

    def traverse_ownership(self, entity_id: str, max_hops: int = 5) -> list[dict]:
        cypher = (
            f"MATCH p = (start {{node_id: $entity_id}})-[:OWNS*1..{max_hops}]->(target) "
            "RETURN [n in nodes(p) | n.id] as node_ids, length(p) as path_length ORDER BY path_length ASC"
        )
        result = self.session.run(cypher, entity_id=entity_id)
        return [{"node_ids": r["node_ids"], "path_length": r["path_length"]} for r in result]

    def check_sanctions(self, entity_id: str) -> list[dict]:
        result = self.session.run(
            "MATCH (entity {node_id: $entity_id})-[:SANCTIONED_BY]->(sanction:Sanction) "
            "RETURN entity.id as entity_id, entity.caption as caption, sanction.id as sanction_id, sanction.dataset as dataset",
            entity_id=entity_id,
        )
        return [{"entity_id": r["entity_id"], "caption": r["caption"], "sanction_id": r["sanction_id"], "dataset": r["dataset"]} for r in result]

    def find_cycles(self, entity_id: str, rel_type: str = "OWNS") -> list[dict]:
        cypher = f"MATCH (start {{node_id: $entity_id}}) MATCH cycle = (start)-[:{rel_type}*2..6]->(start) RETURN [n in nodes(cycle) | n.id] as node_ids, length(cycle) as cycle_length"
        result = self.session.run(cypher, entity_id=entity_id)
        return [{"node_ids": r["node_ids"], "cycle_length": r["cycle_length"], "rel_type": rel_type} for r in result]

    def get_relationships(self, entity_id: str) -> list[dict]:
        result = self.session.run(
            "MATCH (source {node_id: $entity_id})-[r]->(target) "
            "RETURN source.id as source_id, source.caption as source_caption, type(r) as rel_type, target.id as target_id, target.caption as target_caption",
            entity_id=entity_id,
        )
        return [{"source_id": r["source_id"], "source_caption": r["source_caption"], "rel_type": r["rel_type"], "target_id": r["target_id"], "target_caption": r["target_caption"]} for r in result]

    def get_filings(self, entity_id: str) -> list[dict]:
        result = self.session.run(
            "MATCH (entity {node_id: $entity_id})--(filing) WHERE filing.schema IN ['Filing', 'Document'] "
            "RETURN filing.id as filing_id, filing.caption as caption, filing.dataset as dataset",
            entity_id=entity_id,
        )
        return [{"filing_id": r["filing_id"], "caption": r["caption"], "dataset": r["dataset"]} for r in result]

    def get_news(self, entity_id: str) -> list[dict]:
        result = self.session.run(
            "MATCH (entity {node_id: $entity_id})--(news) WHERE news.schema IN ['Article', 'News', 'Media'] "
            "RETURN news.id as news_id, news.caption as caption, news.dataset as dataset",
            entity_id=entity_id,
        )
        return [{"news_id": r["news_id"], "caption": r["caption"], "dataset": r["dataset"]} for r in result]

    def score_jurisdiction(self, iso_code: str) -> dict:
        HIGH = {"kp", "ir", "sy", "cu"}
        MEDIUM = {"ch", "ae", "hk", "ru"}
        code = iso_code.lower()
        score = 90 if code in HIGH else 60 if code in MEDIUM else 20
        level = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
        return {"iso_code": iso_code, "risk_score": score, "risk_level": level}

    def dispatch(self, name: str, input_params: dict[str, Any]) -> Any:
        tool_map = {
            "find_entity": lambda: self.find_entity(**input_params),
            "traverse_ownership": lambda: self.traverse_ownership(**input_params),
            "check_sanctions": lambda: self.check_sanctions(**input_params),
            "find_cycles": lambda: self.find_cycles(**input_params),
            "get_relationships": lambda: self.get_relationships(**input_params),
            "get_filings": lambda: self.get_filings(**input_params),
            "get_news": lambda: self.get_news(**input_params),
            "score_jurisdiction": lambda: self.score_jurisdiction(**input_params),
        }
        if name not in tool_map:
            raise ValueError(f"Unknown tool: {name}")
        return tool_map[name]()

    def schemas(self) -> list[dict]:
        return [
            {"name": "find_entity", "description": "Find entity by fuzzy name match on caption", "input_schema": {"type": "object", "properties": {"name": {"type": "string"}, "limit": {"type": "integer", "default": 5}}, "required": ["name"]}},
            {"name": "traverse_ownership", "description": "Traverse OWNS edges BFS to find UBOs", "input_schema": {"type": "object", "properties": {"entity_id": {"type": "string"}, "max_hops": {"type": "integer", "default": 5}}, "required": ["entity_id"]}},
            {"name": "check_sanctions", "description": "Find SANCTIONED_BY connections", "input_schema": {"type": "object", "properties": {"entity_id": {"type": "string"}}, "required": ["entity_id"]}},
            {"name": "find_cycles", "description": "Detect circular paths", "input_schema": {"type": "object", "properties": {"entity_id": {"type": "string"}, "rel_type": {"type": "string", "default": "OWNS"}}, "required": ["entity_id"]}},
            {"name": "get_relationships", "description": "Get all connected entities", "input_schema": {"type": "object", "properties": {"entity_id": {"type": "string"}}, "required": ["entity_id"]}},
            {"name": "get_filings", "description": "Get Filing/Document nodes", "input_schema": {"type": "object", "properties": {"entity_id": {"type": "string"}}, "required": ["entity_id"]}},
            {"name": "get_news", "description": "Get news/media nodes", "input_schema": {"type": "object", "properties": {"entity_id": {"type": "string"}}, "required": ["entity_id"]}},
            {"name": "score_jurisdiction", "description": "Jurisdiction risk score", "input_schema": {"type": "object", "properties": {"iso_code": {"type": "string"}}, "required": ["iso_code"]}},
        ]
