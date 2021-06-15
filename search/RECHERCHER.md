Recherches
========

### Modules potentiellement utile

- [SPARQLWrapper]{https://sparqlwrapper.readthedocs.io/en/latest/main.html} Le module permet de faire et de récupérer
  des requêtes SPARQL sur une base de donnée.
  ```python
  from SPARQLWrapper import SPARQLWrapper
  
  endpoint: str = "http://kaiko.getalp.org/sparql"  # Set endpoint  
  statement: str = """ SELECT ?n WHERE {?n rdf:type qb:DataSet} """  # Set the statement
  
  sparql: SPARQLWrapper = SPARQLWrapper(endpoint)  # Initialize the connection
  sparql.setQuery(statement)  # Set the query with the statement
  sparql.setReturnFormat('json')  # Set the return format
  
  results: dict = sparql.query().convert()  # Do the request
  
  print(results) # Display results of request
  ```
- [rdflib]{https://rdflib.readthedocs.io/en/stable/} Module permettant de naviguer parmi des données RDF.
  ```python
  import rdflib

  uri: str = "http://kaiko.getalp.org/dbnary/statistics/dbnaryNymRelationsCube"
  g = rdflib.Graph()  # create a Graph
  result: rdflib.Graph = g.parse(uri)  # parse in an RDF file hosted on the Internet

  print(g.serialize(format="turtle").decode("utf-8"))  # print out the entire Graph in the RDF Turtle format
  ```
- [urllib] Module permettant de faire des requêtes HTML.
  ```python
  import urllib

  uri: str = "http://kaiko.getalp.org/dbnary#dbnaryNymRelationsDataStructure"  # The URI for the data you want to fetch
  request_headers: dict = {'Accept': 'application/rdf+xml'}  # The content type you want to set in the Request Headers.
  
  request = urllib.request.Request(uri, headers = request_headers)  # Build the request with the URI and Header parameters 
  response = urllib.request.urlopen(request)  # Fetch the request
  data: str = response.read().decode('utf8') # Read and Print the request

  print(data)
  ```
