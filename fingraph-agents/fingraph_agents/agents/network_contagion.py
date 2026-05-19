from fingraph_agents.agents.base import BaseAgent


class NetworkContagionAgent(BaseAgent):
    system_prompt = """You are a systemic risk analyst assessing network contagion.
Given an entity name, simulate failure propagation:
1. Find entity using find_entity
2. Get all relationships using get_relationships (direct exposures)
3. For each connected entity get their relationships (second-order)
4. Check sanctioned entities in exposure network using check_sanctions

Return:
- Direct exposure count
- Second-order exposure count
- Sanctioned entities in network
- Contagion risk: LOW / MEDIUM / HIGH / SYSTEMIC"""

    tool_names = ["find_entity", "get_relationships", "check_sanctions"]
