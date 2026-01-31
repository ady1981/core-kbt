from rdflib import Graph

from common import read_string
from kg_common import calc_all_classes, calc_instance_classes, calc_subclasses

g = Graph()

data = read_string("examples/difference_ontology.ttl") + '\n' + read_string("temp/with-kg/demo2.ttl")

g.parse(data=data, format="turtle")

print(f"=== Successfully loaded {len(g)} triples ---")

# g.serialize(destination="temp/with-kg/output.ttl", format='turtle')

LOCAL_DOMAIN = 'file://domain_knowledge'


def split_namespace_name(uri_value):
    if '#' in uri_value:
        uri_parts = uri_value.split('#')
        namespace = uri_parts[0]
        if namespace == LOCAL_DOMAIN:
            namespace = ':'
        return [namespace, uri_parts[-1]]
    else:
        return ['', uri_value]


def short_name(uri_value):
    [namespace, id] = split_namespace_name(uri_value)
    if namespace:
        return '#'.join([namespace, id])
    else:
        return f'\'{uri_value}\''


def print_graph():
    for s, p, o in g.triples((None, None, None)):
        print(f"{short_name(s)} | {short_name(p)} | {short_name(o)}")


print_graph()

# sparql_query = read_string('temp/with-kg/demo1_query.sparql')
# results = g.query(sparql_query)
# # Process the results
# print("--- SELECT Query Results ---")
# for row in results:
#     print(', '.join(f'{c}: {short_name(row[c])}' for c in row.labels))

##

classes = calc_all_classes(g)
print('=== classes:', [short_name(c) for c in classes])

instance_classes = calc_instance_classes(g, classes)
print('=== instances by class:')
for c in classes:
    if instance_classes.get(c) is not None:
        print(f'--- class: {short_name(c)}', [short_name(c) for c in instance_classes.get(c)])

print('=== subclasses by class:')
for c in classes:
    print(f'--- class: {short_name(c)}', [short_name(c) for c in calc_subclasses(g, c)])
