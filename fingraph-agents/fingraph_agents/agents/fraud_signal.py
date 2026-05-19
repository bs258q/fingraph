from typing import Any
from fingraph_agents.agents.base import BaseAgent


class FraudSignalAgent(BaseAgent):
    system_prompt = """You are a fraud detection specialist analyzing transaction patterns.
Given a company or person name:
1. Find the entity using find_entity
2. Check for circular ownership/transaction paths using find_cycles
3. Examine all relationships using get_relationships for shell company indicators
4. Review filings using get_filings for disclosure gaps

Shell company indicators: high OWNS depth, low filings, offshore jurisdiction, circular structures.

Return:
- Risk score 0-100
- Detected patterns (list)
- Recommended action: PASS / REVIEW / ESCALATE"""

    tool_names = ["find_entity", "find_cycles", "get_relationships", "get_filings"]

    def _parse_structured(self, text: str) -> dict[str, Any]:
        import re
        m = re.search(r"(\d+)/100|score[:\s]+(\d+)", text, re.IGNORECASE)
        score = int(m.group(1) or m.group(2)) if m else 0
        action = "UNKNOWN"
        for a in ["ESCALATE", "REVIEW", "PASS"]:
            if a in text.upper():
                action = a
                break
        return {"risk_score": score, "action": action}
