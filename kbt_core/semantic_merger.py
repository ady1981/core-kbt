def merge_simple_arity2(semantic_equivalence, array1, array2):
    if len(semantic_equivalence['not_comparable_1']) > 0 or len(semantic_equivalence['not_comparable_2']) > 0:
        raise ValueError('not-comparable-for-simple-merge')
    result = [array1[c['_1'][0] - 1] for c in semantic_equivalence['comparable_equal']]
    result += [array1[c[0] - 1] for c in semantic_equivalence['comparable_not_equal_1']]
    result += [array2[c[0] - 1] for c in semantic_equivalence['comparable_not_equal_2']]
    return result
