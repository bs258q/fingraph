"""Tests for schema models."""
from fingraph_core.schema.models import (
    Company, Person, Jurisdiction, SanctionsList,
    OwnsStake, Controls, SanctionedBy, TransactsWith,
    SCHEMA_CONSTRAINTS,
)


def test_company_node_fields() -> None:
    c = Company(node_id="c1", name="Acme Corp", lei="ABCDE12345")
    assert c.node_id == "c1"
    assert c.label == "Company"


def test_person_node_fields() -> None:
    p = Person(node_id="p1", name="John Doe", pep=False)
    assert p.label == "Person"


def test_owns_stake_edge() -> None:
    e = OwnsStake(from_id="p1", to_id="c1", percentage=51.0, source="sec_edgar")
    assert e.edge_type == "OWNS_STAKE"
    assert e.percentage == 51.0


def test_schema_constraints_nonempty() -> None:
    assert len(SCHEMA_CONSTRAINTS) > 0
    assert all(s.startswith("CREATE") for s in SCHEMA_CONSTRAINTS)
