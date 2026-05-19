import json
from typing import Any, Optional
from anthropic import Anthropic
from fingraph_agents.tools.graph_tools import GraphTools
from fingraph_agents.result import AgentResult, ToolCall


class BaseAgent:
    system_prompt: str = ""
    tool_names: list[str] = []
    model: str = "claude-sonnet-4-6"
    max_tokens: int = 4096
    max_iterations: int = 10

    def __init__(self, tools: GraphTools, client: Optional[Anthropic] = None):
        self.tools = tools
        self.client = client or Anthropic()

    async def run(self, query: str) -> AgentResult:
        tool_calls: list[ToolCall] = []
        messages = [{"role": "user", "content": query}]
        response = None

        for iteration in range(self.max_iterations):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    system=self.system_prompt,
                    tools=self.tools.schemas(),
                    messages=messages,
                )
            except Exception as e:
                return AgentResult(
                    query=query, agent_name=self.__class__.__name__,
                    status="FAILED", finding=f"Claude API error: {e}",
                    confidence=0.0, tool_calls=tool_calls,
                    iterations=iteration + 1, error=str(e),
                )

            if response.stop_reason == "end_turn":
                finding = self._extract_finding(response)
                return AgentResult(
                    query=query, agent_name=self.__class__.__name__,
                    status="COMPLETE", finding=finding,
                    confidence=self._estimate_confidence(finding),
                    tool_calls=tool_calls, iterations=iteration + 1,
                )

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        try:
                            output = self.tools.dispatch(block.name, block.input)
                            error = None
                        except Exception as e:
                            output = None
                            error = str(e)
                        tool_calls.append(ToolCall(name=block.name, input=block.input, output=output, error=error))
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(output) if output is not None else f"Error: {error}",
                        })
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})

        finding = (self._extract_finding(response) if response else None) or "Max iterations reached"
        return AgentResult(
            query=query, agent_name=self.__class__.__name__,
            status="TIMEOUT", finding=finding,
            confidence=0.5, tool_calls=tool_calls,
            iterations=self.max_iterations, error="Max iterations reached",
        )

    def _extract_finding(self, response: Any) -> str:
        for block in response.content:
            if hasattr(block, "text") and hasattr(block, "type") and block.type == "text":
                return block.text
        return "No finding generated"

    def _estimate_confidence(self, text: str) -> float:
        return min(0.95, len(text) / 500.0) if text else 0.0

    def _parse_structured(self, text: str) -> dict[str, Any]:
        return {}
