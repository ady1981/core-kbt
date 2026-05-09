from rdflib import RDF, OWL, RDFS


def calc_all_classes(graph):
    """Finds all resources explicitly defined as classes."""
    classes = set()

    # Look for resources typed as owl:Class
    for s, p, o in graph.triples((None, RDF.type, OWL.Class)):
        classes.add(s)

    # Also include resources typed as rdfs:Class (common in RDFS/OWL)
    for s, p, o in graph.triples((None, RDF.type, RDFS.Class)):
        classes.add(s)

    return classes


def calc_instance_classes(graph, classes):
    """Groups all instances by their direct class."""
    taxonomy = {}

    for cls in classes:
        instances = set()
        # Find all subjects (s) where (s, rdf:type, cls) is true
        for s, p, o in graph.triples((None, RDF.type, cls)):
            # Ensure we only capture actual instances, not class definitions themselves
            if s != cls:
                instances.add(s)

        if instances:
            # Use the class URI as the key
            taxonomy[cls] = list(instances)

    return taxonomy


def calc_subclasses(graph, target_class):
    """Recursively finds all direct and indirect subclasses of a target class."""
    subclasses = {target_class}

    # Find direct subclasses
    for s, p, o in graph.triples((None, RDFS.subClassOf, target_class)):
        # s is a subclass of target_class (o)
        subclasses.update(calc_subclasses(graph, s))

    return subclasses
