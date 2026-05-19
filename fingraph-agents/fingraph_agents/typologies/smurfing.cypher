MATCH (source)-[r:OWNS]->(dest)
WITH source, count(dest) as target_count
WHERE target_count > 5
RETURN source.id as source_id, source.caption as caption, target_count
LIMIT 10
