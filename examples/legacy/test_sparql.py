from rdflib import Graph, Literal, URIRef, Namespace, RDF

# 1. Create a Graph instance
g = Graph()

# Define namespaces for cleaner triples
EX = Namespace("http://example.org/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

# 2. Add some sample data (triples)
g.add((EX.alice, RDF.type, FOAF.Person))
g.add((EX.bob, RDF.type, FOAF.Person))
g.add((EX.charlie, RDF.type, FOAF.Person))
g.add((EX.alice, FOAF.name, Literal("Alice")))
g.add((EX.alice, FOAF.knows, EX.bob))
g.add((EX.bob, FOAF.name, Literal("Bob")))
g.add((EX.charlie, FOAF.name, Literal("Charlie")))

# 3. Define the SPARQL query string
sparql_query = """
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX ex: <http://example.org/>

SELECT ?person ?name
WHERE {
    ?person a ?type .  # Selects any subject that is an RDF resource
    ?person foaf:name ?name .
    FILTER (BOUND(?name))
}
ORDER BY ?name
"""

# 4. Execute the query
results = g.query(sparql_query)

# 5. Process the results
print("--- SELECT Query Results ---")
for row in results:
    # Access results by variable name (e.g., row.person, row.name)
    print(f"Person: {row.person.toPython()}, Name: {row.name.toPython()}")