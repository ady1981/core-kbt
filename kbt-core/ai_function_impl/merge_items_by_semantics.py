from functools import reduce

import ai_function_template
from common import first, rest


def merge_arrays(model, left, right, array_item_json_schema, merge_strategy):
    equivalence_items = ai_function_template.evaluate('estimate_arity2_array_criterial_semantic_equivalence', {'meta': {'model': model}, 'array_1': left, 'array_2': right, 'item_json_schema': array_item_json_schema})

    upd_items = []

    # not_comparable
    not_comparable = equivalence_items.get('not_comparable')
    upd_items += [c[1] for c in not_comparable['_1']]
    if merge_strategy.get('not_comparable') == 'merge':
        upd_items += rewrite_items_by_examples(model, [c[1] for c in not_comparable['_2']], left, array_item_json_schema)

    # comparable.equal
    upd_items += [c['_1'][1] for c in equivalence_items.get('comparable', {}).get('equal', [])]

    # comparable.not_equal
    comparable_not_equal = equivalence_items.get('comparable', {}).get('not_equal', {})
    upd_items += [c[1] for c in comparable_not_equal['_1']]
    if merge_strategy.get('comparable_not_equal') == 'merge':
        upd_items += rewrite_items_by_examples(model, [c[1] for c in comparable_not_equal['_2']], left, array_item_json_schema)

    return upd_items


async def evaluate(input_data):
    ## TODO: check input schema
    array_item_json_schema = input_data['array_item_json_schema']
    arrays = input_data['arrays']
    merge_strategy = input_data['merge_strategy']
    meta = input_data.get('meta', {})
    model = meta.get('model', None)
    first_array = first(arrays)
    rest_arrays = rest(arrays)
    result = reduce(lambda acc, c: merge_arrays(model, acc, c, array_item_json_schema, merge_strategy) if c is not None else c, rest_arrays, first_array) ## upd_array
    return result


def rewrite_items_by_examples(model, items, example_items, array_item_json_schema):
    if isinstance(array_item_json_schema['items'], list):
        item_json_schema = array_item_json_schema['items'][0]
    else:
        item_json_schema = array_item_json_schema['items']
    context = item_json_schema['description']
    r = [ai_function_template.evaluate('rewrite_thing_by_examples', {
        'meta': {'model': model},
        'context': context,
        'item': c,
        'examples': example_items
    })['rewritten_item'] for c in items]
    return r
