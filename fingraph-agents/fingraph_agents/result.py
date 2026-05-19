from pydantic import BaseModel, Field
from typing import Any, Optional


class ToolCall(BaseModel):
    name: str
    input: dict[str, Any] = Field(default_factory=dict)
    output: Any = None
    error: Optional[str] = None


class GraphPath(BaseModel):
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    length: int


class AgentResult(BaseModel):
    query: str
    agent_name: str
    status: str  # COMPLETE|FAILED|TIMEOUT
    finding: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    tool_calls: list[ToolCall] = Field(default_factory=list)
    iterations: int = 0
    error: Optional[str] = None
