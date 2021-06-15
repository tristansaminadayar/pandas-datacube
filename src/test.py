from SPARQLWrapper import SPARQLWrapper
import rdflib

endpoint: str = "http://kaiko.getalp.org/sparql"
statement: str = """
SELECT DISTINCT ?values
WHERE {?t rdf:type qb:DataSet .
       ?values qb:dataSet ?t .
}
"""

sparql: SPARQLWrapper = SPARQLWrapper(endpoint)
sparql.setQuery(statement)  # Link to query
sparql.setReturnFormat("json")  # Set return format of query to JSON

results: dict = sparql.query().convert()  # Get the result of the query

values = [item['values']['value'] for item in results['results']['bindings']]

print(values)

# create a Graph
g = rdflib.Graph()

for item in values:
    # parse in an RDF file hosted on the Internet
    result = g.parse(item)

    # loop through each triple in the graph (subj, pred, obj)
    for subj, pred, obj in g:
        # check if there is at least one triple in the Graph
        pass
        # print(subj, pred, obj)

    # print out the entire Graph in the RDF Turtle format
    print(g.serialize(format="turtle").decode("utf-8"))
