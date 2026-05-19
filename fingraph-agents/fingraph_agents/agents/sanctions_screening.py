from typing import Any
from fingraph_agents.agents.base import BaseAgent


class SanctionsScreeningAgent(BaseAgent):
    system_prompt = """You are a sanctions screening specialist.
Given a list of entity names, for each entity:
1. Find it using find_entity
2. Check for sanctions using check_sanctions
3. Check close associates (1 hop via get_relationships) if initial check is clean

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
