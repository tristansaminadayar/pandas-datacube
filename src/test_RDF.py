import rdflib

# create a Graph
g = rdflib.Graph()

# parse in an RDF file hosted on the Internet
result = g.parse('http://kaiko.getalp.org/describe/?url=http%3A%2F%2Fkaiko.getalp.org%2Fdbnary%23dbnaryNymRelationsDataStructure')

# loop through each triple in the graph (subj, pred, obj)
for subj, pred, obj in g:
    # check if there is at least one triple in the Graph
    if (subj, pred, obj) not in g:
       raise Exception("It better be!")

# print the number of "triples" in the Graph
print("graph has {} statements.".format(len(g)))
# prints graph has 86 statements.

# print out the entire Graph in the RDF Turtle format
print(g.serialize(format="turtle").decode("utf-8"))