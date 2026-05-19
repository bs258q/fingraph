"""Graph node and edge models for Neo4j."""
from pydantic import BaseModel, model_validator
from typing import Optional, Self
import re


class GraphNode(BaseModel):
    """Base class for all graph nodes."""
    node_id: str
    label: str = ""
    source: str = ""

    @model_validator(mode='after')
    def set_label(self) -> Self:
        """Set label to class name if not provided."""
        if not self.label:
            object.__setattr__(self, 'label', self.__class__.__name__)
        return self


class Company(GraphNode):
    """Company node."""
    name: str
    lei: Optional[str] = None
    ein: Optional[str] = None
    isin: Optional[str] = None
    jurisdiction: Optional[str] = None
    active: bool = True


class Person(GraphNode):
    """Person node."""
    name: str
    pep: bool = False
    nationality: Optional[str] = None
    dob: Optional[str] = None


class Jurisdiction(GraphNode):
    """Jurisdiction node."""
    name: str
    iso_code: str
    risk_score: float = 0.0


class SanctionsList(GraphNode):
    """Sanctions list node."""
    name: str
    issuer: str


class NewsArticle(GraphNode):
    """News article node."""
    url: str
    title: str
    published: str
    category: str = ""


class GraphEdge(BaseModel):
    """Base class for all graph edges."""
    from_id: str
    to_id: str
    edge_type: str = ""
    source: str = ""

    @model_validator(mode='after')
    def set_edge_type(self) -> Self:
        """Set edge_type to class name in UPPER_SNAKE_CASE if not provided."""
        if not self.edge_type:
            # Convert camelCase to UPPER_SNAKE_CASE
            class_name = self.__class__.__name__
            snake_case = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', class_name)
            edge_type = re.sub('([a-z0-9])([A-Z])', r'\1_\2', snake_case).upper()
            object.__setattr__(self, 'edge_type', edge_type)
        return self


class OwnsStake(GraphEdge):
    """Edge representing ownership stake."""
    percentage: Optional[float] = None


class Controls(GraphEdge):
    """Edge representing control relationship."""
    control_type: str = "direct"


class SanctionedBy(GraphEdge):
    """Edge representing sanctions listing."""
    listed_date: Optional[str] = None
    reason: Optional[str] = None


class TransactsWith(GraphEdge):
    """Edge representing transaction relationship."""
    volume: Optional[float] = None
    frequency: Optional[int] = None


class RegisteredIn(GraphEdge):
    """Edge representing registration relationship."""
    pass


class MentionedIn(GraphEdge):
    """Edge representing mention in article."""
    sentiment: str = "neutral"


SCHEMA_CONSTRAINTS = [
    "CREATE CONSTRAINT company_id IF NOT EXISTS FOR (c:Company) REQUIRE c.node_id IS UNIQUE",
    "CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.node_id IS UNIQUE",
    "CREATE CONSTRAINT jurisdiction_id IF NOT EXISTS FOR (j:Jurisdiction) REQUIRE j.node_id IS UNIQUE",
    "CREATE CONSTRAINT sanctions_id IF NOT EXISTS FOR (s:SanctionsList) REQUIRE s.node_id IS UNIQUE",
    "CREATE CONSTRAINT news_id IF NOT EXISTS FOR (n:NewsArticle) REQUIRE n.node_id IS UNIQUE",
    "CREATE INDEX company_lei IF NOT EXISTS FOR (c:Company) ON (c.lei)",
    "CREATE INDEX company_ein IF NOT EXISTS FOR (c:Company) ON (c.ein)",
    "CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name)",
]
