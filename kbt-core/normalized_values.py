def with_normalized_value(items: list[dict], value_field: str, normalized_prefix: str, score_field: str, items_external_weight = 1.0):
    total_score = sum(c[score_field] for c in items)
    for c in items:
        c[f'{normalized_prefix}{value_field}'] = c[value_field] * (c[score_field] / total_score) * items_external_weight
    return (total_score * items_external_weight, items)
