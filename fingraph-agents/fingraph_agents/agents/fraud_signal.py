from typing import Any
from fingraph_agents.agents.base import BaseAgent


class FraudSignalAgent(BaseAgent):
    system_prompt = """You are a fraud detection specialist analyzing transaction patterns.
Given a company or person name:
1. Call find_entity ONCE to resolve entity ID
2. Call find_cycles ONCE — returns all circular paths in one query
3. Call get_relationships ONCE — returns all connections
4. Call get_filings ONCE — do NOT call again for connected entities

EFFICIENCY RULES — max 4 tool calls total:
- Never repeat any tool call for the same entity ID
- find_cycles and get_relationships already return full results — do not loop

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
