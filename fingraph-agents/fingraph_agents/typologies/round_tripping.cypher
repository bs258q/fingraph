MATCH cycle = (a)-[:OWNS*2..6]->(a)
RETURN [n in nodes(cycle) | n.id] as cycle_nodes, length(cycle) as hops
LIMIT 10
