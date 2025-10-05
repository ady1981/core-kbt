from functools import reduce

import ai_function_template
from common import first, rest, with_model_input_data


def merge_arrays(model, left, right, array_item_json_schema, merge_strategy):
    equivalence_items = ai_function_template.evaluate('estimate_arity2_array_criterial_semantic_equivalence', with_model_input_data({'array_1': left, 'array_2': right, 'item_json_schema': array_item_json_schema}, model))

    upd_items = []

    # not_comparable
    not_comparable = equivalence_items.get('not_comparable', {})
    upd_items += [c[1] for c in not_comparable.get('_1', [])]
    if merge_strategy.get('not_comparable') == 'merge':
        upd_items += rewrite_items_by_examples(model, [c[1] for c in not_comparable.get('_2', [])], left, array_item_json_schema)

    # comparable.equal
    upd_items += [c['_1'][1] for c in equivalence_items.get('comparable', {}).get('equal', [])]

    # comparable.not_equal
    comparable_not_equal = equivalence_items.get('comparable', {}).get('not_equal', {})
    upd_items += [c[1] for c in comparable_not_equal.get('_1', [])]
    if merge_strategy.get('comparable_not_equal') == 'merge':
        upd_items += rewrite_items_by_examples(model, [c[1] for c in comparable_not_equal.get('_2', [])], left, array_item_json_schema)

    return upd_items


async def evaluate(input_data):
    ## TODO: check input schema
    arrays = input_data['arrays']
    array_item_json_schema = input_data['array_item_json_schema']
    merge_strategy = input_data['merge_strategy']
    meta = input_data.get('meta', {})
    model = meta.get('model', None)
    first_array = first(arrays)
    rest_arrays = rest(arrays)
    upd_array = reduce(lambda acc, c: merge_arrays(model, acc, c, array_item_json_schema, merge_strategy) if c is not None else c, rest_arrays, first_array)
    # upd_array2 = split_and_merge_items(model, upd_array, array_item_json_schema)
    return upd_array


def calc_context(array_item_json_schema):
    if isinstance(array_item_json_schema['items'], list):
        item_json_schema = array_item_json_schema['items'][0]
    else:
        item_json_schema = array_item_json_schema['items']
    context = item_json_schema['description']
    return context


def rewrite_items_by_examples(model, items, example_items, array_item_json_schema):
    context = calc_context(array_item_json_schema)
    r = [ai_function_template.evaluate('rewrite_thing_by_examples', with_model_input_data({
        'context': context,
        'item': c,
        'examples': example_items
    }, model))['rewritten_item'] for c in items]
    return r


# def split_and_merge_items(model, items, array_item_json_schema):
#     ai_fun_name = 'split_and_merge_items'
#     template_string = read_string(f'ai_function_templates/{ai_fun_name}/prompt.md.j2')
#     context = calc_context(array_item_json_schema)
#     data = with_model_input_data({
#         'context': context,
#         'list_of_items': items
#     },
#         model)
#     instruction = render_template(template_string, data)
#     log_str(f'instruction:\n{instruction}')
#     response_schema = read_yaml(f'ai_function_templates/{ai_fun_name}/output_schema.yaml')
#     response = ai_function_template.evaluate2(instruction, response_schema, model=model)
#     if response.get('json', {}).get('final_rebuilt_list', False):
#         return response.get('json').get('final_rebuilt_list')
#     else:
#         log_str('cannot split_and_merge_items')
#         return items
