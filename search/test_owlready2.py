from owlready2 import *

try:  # Plante lors du premier appel
    onto = get_ontology("http://kaiko.getalp.org/dbnary").load()
except owlready2.base.OwlReadyOntologyParsingError:
    pass
onto: owlready2.namespace.Ontology = get_ontology("http://kaiko.getalp.org/dbnary").load()  # Load the ontology

print(list(onto.individuals()))  # Displays the individuals

print(list(onto.classes()))  # Display the classes

liste = onto.search(iri="*Structure*")
print(liste)

a = liste[1]
print(a.comment)
print(a.get_iri())
