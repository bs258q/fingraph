from typing import Any
from fingraph_agents.agents.base import BaseAgent


class KYCAgent(BaseAgent):
    system_prompt = """You are a KYC (Know Your Customer) compliance specialist.
Given a company or person name, your job is to:
1. Find the entity using find_entity
2. Traverse ownership chain using traverse_ownership to find Ultimate Beneficial Owners (UBOs)
3. Check each entity in the chain for sanctions using check_sanctions
4. Score jurisdiction risk using score_jurisdiction for relevant countries

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
