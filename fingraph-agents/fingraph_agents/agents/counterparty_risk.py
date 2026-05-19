from typing import Any
from fingraph_agents.agents.base import BaseAgent


class CounterpartyRiskAgent(BaseAgent):
    system_prompt = """You are a counterparty risk analyst.
Given an entity name:
1. Find entity using find_entity
2. Get all relationships using get_relationships
3. Check sanctions on entity and key counterparties using check_sanctions
4. Score jurisdiction risk using score_jurisdiction
5. Review filings using get_filings for material risk disclosures

Return:
- Exposure summary (relationship count and types)
- Sanctions exposure (any sanctioned counterparties)
- Jurisdiction risk (highest risk jurisdiction found)
- Overall rating: LOW / MEDIUM / HIGH / CRITICAL"""

    tool_names = ["find_entity", "get_relationships", "check_sanctions", "score_jurisdiction", "get_filings"]
