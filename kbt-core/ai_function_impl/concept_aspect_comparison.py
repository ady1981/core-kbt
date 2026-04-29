from functools import reduce

import ai_function_template
from common import with_model_input_data, index_by, with_key


def calc_perspective_aspects(model, concept, observer_context_description, frame_of_reference):
    perspective_features_resp = ai_function_template.evaluate('perspective_features', with_model_input_data(
        {
            'concept': concept,
            'observer_context_description': observer_context_description,
            'frame_of_reference': frame_of_reference,
        }, model))
    perspective_observer_strategy = perspective_features_resp['perspective_observer_strategy_name']
    point_of_view = perspective_features_resp['point_of_view_name']
    perspective_aspects = perspective_features_resp['perspective_aspects']
    return (perspective_observer_strategy, point_of_view, perspective_aspects)


def with_feature_comparison(aspect, a_concept, b_concept, model, observer_strategy, point_of_view, frame_of_reference):
    aspect_name = aspect['aspect_name']
    aspect_features = index_by(lambda c: c["feature_name"], aspect['aspect_features'])
    aspect_features_coll = '\n'.join([f'- {c}' for c in aspect_features.keys()])
    input_data = with_model_input_data({
        'a_concept': a_concept,
        'b_concept': b_concept,
        'aspect_name': aspect_name,
        'aspect_features': aspect_features_coll,
        'frame_of_reference': frame_of_reference,
        'observer_strategy': observer_strategy,
        'point_of_view': point_of_view
    }, model)
    perspective_feature_comparisons = ai_function_template.evaluate('perspective_feature_comparison', input_data)
    for c in perspective_feature_comparisons["aspect_feature_value_comparison"]:
      feature_name = c.get("feature_name", '')
      if aspect_features.get(feature_name):
          aspect_features[feature_name]['comparison'] = c.get('comparison', 0)
    return with_key(aspect, "aspect_features", aspect_features.values())


def calc_total_score(perspective_aspects):
    return reduce(lambda acc, c: acc + c["aspect_importance_score_to_other_aspects"], perspective_aspects, 0)


def with_aspect_comparison(aspect, total_score):
    aspect_features = aspect["aspect_features"]
    aspect_features_total_score = reduce(lambda acc, c: acc + c.get("feature_importance_score_to_other_features", 1), aspect_features, 0)
    aspect_features2 = [with_key(c,
                                 'normalized_comparison',
                                 c['comparison']
                                 * (c.get("feature_importance_score_to_other_features", 1) / aspect_features_total_score)
                                 * (aspect.get("aspect_importance_score_to_other_aspects", 1) / total_score))
                        for c in aspect_features]
    aspect_normalized_comparison = reduce(lambda acc, c: acc + c['normalized_comparison'], aspect_features2, 0)
    aspect["aspect_features"] = aspect_features2
    aspect["normalized_comparison"] = aspect_normalized_comparison
    return aspect


def with_total_comparison(perspective_aspects):
    # perspective_aspects = perspective_aspects["aspect_features"]
    total_score = calc_total_score(perspective_aspects)
    perspective_aspects2 = [with_aspect_comparison(c, total_score) for c in perspective_aspects]
    comparison_total = reduce(lambda acc, c: acc + c["normalized_comparison"], perspective_aspects2, 0)
    return (comparison_total, perspective_aspects2)


def calc_genus_concept(model, a_concept, b_concept, observer_context_description):
    concepts = f'- {a_concept}\n- {b_concept}'
    context_knowledge_specification = f'### Context description\n{observer_context_description}'
    genus_concept_identification_resp = ai_function_template.evaluate('genus_concept_identification', with_model_input_data(
        {
            'concepts': concepts,
            'context_knowledge_specification': context_knowledge_specification
        }, model))
    return genus_concept_identification_resp['genus_concept']


async def evaluate(input_data):
    meta = input_data.get('meta', {})
    model = meta.get('model', None)
    (observer_context_description, a_concept, b_concept, frame_of_reference) = (input_data['observer_context_description'], input_data['a_concept'], input_data['b_concept'], input_data['frame_of_reference'])
    genus_concept = calc_genus_concept(model, a_concept, b_concept, observer_context_description)
    (perspective_observer_strategy, point_of_view, perspective_aspects) = calc_perspective_aspects(model,
                                                                                                   genus_concept,
                                                                                                   observer_context_description,
                                                                                                   frame_of_reference)
    perspective_aspects2 = [with_feature_comparison(c, a_concept, b_concept, model, perspective_observer_strategy, point_of_view, frame_of_reference) for c in perspective_aspects]
    (comparison_total, perspective_aspects3) = with_total_comparison(perspective_aspects2)
    return {
        'perspective_observer_strategy': perspective_observer_strategy,
        'point_of_view': point_of_view,
        'comparison_total': comparison_total,
        'comparison_winner': a_concept if comparison_total > 0 else (b_concept if comparison_total < 0 else None),
        'perspective_aspects': perspective_aspects3
    }
