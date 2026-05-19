MATCH path = (origin)-[:OWNS*3..8]->(final)
WHERE origin.id <> final.id AND length(path) > 3
RETURN [n in nodes(path) | n.id] as layer_nodes, length(path) as depth
LIMIT 10
