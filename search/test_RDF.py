import rdflib

uri: str = 'http://kaiko.getalp.org/dbnary/statistics/dbnaryNymRelationsCube'
g = rdflib.Graph()  # create a Graph
result: rdflib.Graph = g.parse(uri)  # parse in an RDF file hosted on the Internet

print(g.serialize(format="turtle").decode("utf-8"))  # print out the entire Graph in the RDF Turtle format
