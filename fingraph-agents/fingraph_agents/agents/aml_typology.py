import json
from pathlib import Path
from typing import Any
from fingraph_agents.agents.base import BaseAgent
from fingraph_agents.tools.graph_tools import GraphTools
from fingraph_agents.result import AgentResult


TYPOLOGIES_DIR = Path(__file__).parent.parent / "typologies"


class AMLTypologyAgent(BaseAgent):
    system_prompt = """You are an AML (Anti-Money Laundering) typology specialist.
Given an entity name and typology pattern scan results, identify matching laundering patterns.

For each matched typology return:
- Typology name
- Confidence (0.0-1.0)
- Evidence (entity IDs involved)
- Escalation level: MONITOR / SUSPICIOUS_ACTIVITY_REPORT / URGENT"""

    tool_names = ["find_entity", "find_cycles", "get_relationships"]

    def __init__(self, tools: GraphTools, client=None):
        super().__init__(tools, client)
        self._typologies = self._load_typologies()

    def _load_typologies(self) -> dict[str, str]:
        patterns: dict[str, str] = {}
        if TYPOLOGIES_DIR.exists():
            for f in TYPOLOGIES_DIR.glob("*.cypher"):
                patterns[f.stem] = f.read_text()
        return patterns

    async def run(self, query: str) -> AgentResult:
        pattern_results: dict[str, list] = {}
        for name, cypher in self._typologies.items():
            try:
                result = self.tools.session.run(cypher)
                pattern_results[name] = [dict(r) for r in result]
            except Exception:
                pattern_results[name] = []

        enriched = query + "\n\nTypology scan results:\n"
        for name, results in pattern_results.items():
            enriched += f"\n{name}: {len(results)} matches"
            if results:
                enriched += f" — sample: {results[0]}"

        return await super().run(enriched)
