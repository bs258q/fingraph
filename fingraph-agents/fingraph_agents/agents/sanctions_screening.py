from typing import Any
from fingraph_agents.agents.base import BaseAgent


class SanctionsScreeningAgent(BaseAgent):
    system_prompt = """You are a sanctions screening specialist.
Given a list of entity names, for each entity:
1. Call find_entity ONCE per name
2. Call check_sanctions ONCE per resolved entity ID
3. Only call get_relationships if check_sanctions is CLEAR AND entity is high-risk — not for every entity

EFFICIENCY RULES:
- 2 tool calls per entity max (find + check)
- Only add get_relationships for entities that are CLEAR but flagged as high-risk by context
- Never re-lookup an entity ID you already have

Return per-entity results:
- HIT: entity found on sanctions list (include which datasets)
- POSSIBLE HIT: fuzzy match found, manual review required
- CLEAR: not found on any sanctions list
- NOT FOUND: entity not in graph

Include confidence per result. Flag HIGH confidence hits prominently."""

    tool_names = ["find_entity", "check_sanctions", "get_relationships"]

    def _parse_structured(self, text: str) -> dict[str, Any]:
        hits = text.upper().count("HIT")
        clears = text.upper().count("CLEAR")
        return {"hits": hits, "clears": clears, "narrative": text}
