MATCH (a)-[:OWNS]->(b)
WHERE a.dataset IS NOT NULL AND b.dataset IS NOT NULL AND a.dataset <> b.dataset
RETURN a.id as source, b.id as target, a.dataset as source_dataset, b.dataset as target_dataset
LIMIT 10
