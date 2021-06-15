import urllib
import rdflib

uri: str = 'http://kaiko.getalp.org/dbnary#dbnaryNymRelationsDataStructure'  # The URI for the data you want to fetch
request_headers: dict = {'Accept': 'application/rdf+xml'}  # The content type you want to set in the Request Headers.

request = urllib.request.Request(uri, headers=request_headers)  # Build the request with the URI and Header parameters
response = urllib.request.urlopen(request)  # Fetch the request
data: str = response.read().decode('utf8')  # Read and Print the request

print(data)

g = rdflib.Graph()  # Create a RDF graph

g.parse(data=data, format='xml')  # Parse the data

print(g.serialize(format="turtle").decode("utf-8"))  # Display data
