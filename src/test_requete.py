from SPARQLWrapper import SPARQLWrapper, JSON

endpoint: str = "http://kaiko.getalp.org/sparql"
statement: str = """
SELECT ?n
WHERE {?n rdf:type qb:DataSet}
LIMIT 100
"""

sparql: SPARQLWrapper = SPARQLWrapper(endpoint)
sparql.setQuery(statement)  # Link to query

sparql.setReturnFormat(JSON)

results = sparql.query().convert()

print(results)
