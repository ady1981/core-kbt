from functools import reduce

import ai_function


def merge_arrays(left, right, item_json_schema):
    equivalence_items = ai_function.evaluate('estimate_arity2_array_criterial_semantic_equivalence', {'array_1': left, 'array_2': right, 'item_json_schema': item_json_schema})

    ##TODO: rewrite items
    result = ai_function.evaluate('rewrite_thing_by_examples', {
        'context': 'Task types for LLM',
        'item': 'TextRewritingTask',
        'examples': ['codeGeneration', 'conversationalAgent', 'questionAnswering']
    })
    ##TODO: merge


def evaluate(input_data):
    ## TODO: check input schema
    item_json_schema = input_data['item_json_schema']
    arrays = input_data['arrays']
    merge_strategy = input_data['merge_strategy']
    meta = input_data['meta']
    result = reduce(lambda acc, c: merge_arrays(acc, c, item_json_schema) if c is not None else c, arrays, None)
    return result
