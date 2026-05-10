import os

DEFAULT_VALUE = 0
DEFAULT_SCORE = float(os.getenv('KBT_DEFAULT_SCORE')) if os.getenv('KBT_DEFAULT_SCORE') is not None else 1.0

def with_normalized_value(items: list[dict], value_field: str, normalized_prefix: str, score_field: str, items_external_weight = 1.0):
    total_score = sum(c.get(score_field, DEFAULT_SCORE) for c in items)
    for c in items:
        c[f'{normalized_prefix}{value_field}'] = c.get(value_field, DEFAULT_VALUE) * (c.get(score_field, DEFAULT_SCORE) / total_score) * items_external_weight
    return (total_score * items_external_weight, items)
