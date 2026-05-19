from typing import Any
from fingraph_agents.agents.base import BaseAgent


class AdverseMediaAgent(BaseAgent):
    system_prompt = """You are an adverse media screening specialist.
Given an entity name:
1. Find entity using find_entity
2. Retrieve news articles using get_news
3. Check key related entities for news (from get_relationships)

Classify articles: fraud | money_laundering | bribery | regulatory_action | other

Return:
- Article count by category
- Timeline of adverse events
- Severity: LOW / MEDIUM / HIGH
- Source links"""

    tool_names = ["find_entity", "get_news", "get_relationships"]

    def _parse_structured(self, text: str) -> dict[str, Any]:
        severity = "UNKNOWN"
        for s in ["HIGH", "MEDIUM", "LOW"]:
            if s in text.upper():
                severity = s
                break
        return {"severity": severity}
