from SPARQLWrapper import SPARQLWrapper

endpoint: str = "http://kaiko.getalp.org/sparql"  # Set endpoint
statement: str = """ SELECT ?n WHERE {?n rdf:type qb:DataSet} """  # Set the statement

sparql: SPARQLWrapper = SPARQLWrapper(endpoint)  # Initialize the connection
sparql.setQuery(statement)  # Set the query with the statement
sparql.setReturnFormat('json')  # Set the return format

results: dict = sparql.query().convert()  # Do the request

print(results)  # Display results of request
