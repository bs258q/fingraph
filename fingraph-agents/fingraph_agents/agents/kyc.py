from typing import Any
from fingraph_agents.agents.base import BaseAgent


class KYCAgent(BaseAgent):
    system_prompt = """You are a KYC (Know Your Customer) compliance specialist.
Given a company or person name, your job is to:
1. Call find_entity ONCE to resolve the entity ID
2. Call traverse_ownership ONCE with max_hops=5 — this returns the full chain in one query, do NOT call it again
3. Call check_sanctions ONCE per unique entity ID returned in the chain — batch mentally, no repeat lookups
4. Call score_jurisdiction ONCE per unique jurisdiction in the chain

EFFICIENCY RULES — minimize tool calls:
- Never call find_entity more than once for the same name
- Never call traverse_ownership more than once per subject entity
- If you already have an entity ID from a previous tool result, use it directly — do not re-lookup
- Target: complete in 4-6 tool calls total

Return a structured report:
- List all UBOs (name, path to subject company)
- Flag any sanctioned entities in the ownership chain
- Overall risk: LOW / MEDIUM / HIGH
- Confidence level

Be precise. If entity not found, say so clearly."""

    tool_names = ["find_entity", "traverse_ownership", "check_sanctions", "score_jurisdiction"]

    def _parse_structured(self, text: str) -> dict[str, Any]:
        risk = "UNKNOWN"
        for level in ["HIGH", "MEDIUM", "LOW"]:
            if level in text.upper():
                risk = level
                break
        return {"risk_level": risk, "narrative": text}

    def _estimate_confidence(self, text: str) -> float:
        if "not found" in text.lower():
            return 0.3
        if "HIGH" in text or "MEDIUM" in text or "LOW" in text:
            return 0.85
        return min(0.75, len(text) / 500.0)
