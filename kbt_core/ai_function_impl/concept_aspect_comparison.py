from functools import reduce

from kbt_core.common import with_model_input_data, index_by, with_key, log_str, async_map, dump_json, get_float
from kbt_core.normalized_values import with_normalized_value
from kbt_core.process import execute_process


async def evaluate_via_process(func_name, input_data):
    process_input = input_data
    process_input['process_type'] = f'{func_name}_af'
    process_inputs = [process_input]
    process_results = await async_map(execute_process, process_inputs)
    try:
        return process_results[0]['state']['response']
    except KeyError as e:
        log_str(f"Error: process_results:\n" + dump_json(process_results))
        raise e


async def calc_perspective_aspects(model, concept, observer_context_description, frame_of_reference, output_content_language, extra_information_retrieval_strategy):
    information_retrieval_strategy = f'# Information retrieval strategy\n{extra_information_retrieval_strategy}'
    perspective_features_resp = await evaluate_via_process('perspective_features', with_model_input_data(
        with_extra_output_specification({
            'concept': concept,
            'observer_context_description': observer_context_description,
            'frame_of_reference': frame_of_reference,
            '_information_retrieval_strategy': information_retrieval_strategy
        }, output_content_language), model))
    if perspective_features_resp.get('other_notes'):
        log_str(f'other_notes: {perspective_features_resp.get("other_notes", "")}')
    perspective_observer_strategy = perspective_features_resp['perspective_observer_strategy_name']
    point_of_view = perspective_features_resp['point_of_view_name']
    perspective_aspects = perspective_features_resp['perspective_aspects']
    return (perspective_observer_strategy, point_of_view, perspective_aspects)


async def with_feature_comparison(aspect, a_concept, b_concept, model, observer_strategy, point_of_view, frame_of_reference, output_content_language, extra_information_retrieval_strategy):
    aspect_name = aspect['aspect_name']
    aspect_features = index_by(lambda c: c["feature_name"], aspect['aspect_features'])
    aspect_features_coll = '\n'.join([f'- {c}' for c in aspect_features.keys()])
    information_retrieval_strategy = f'# Information retrieval strategy\n{extra_information_retrieval_strategy}'
    input_data = with_model_input_data(with_extra_output_specification({
        'a_concept': a_concept,
        'b_concept': b_concept,
        'aspect_name': aspect_name,
        'aspect_features': aspect_features_coll,
        'frame_of_reference': frame_of_reference,
        'observer_strategy': observer_strategy,
        'point_of_view': point_of_view,
        '_information_retrieval_strategy': information_retrieval_strategy
    }, output_content_language), model)
    perspective_feature_comparisons_resp = await evaluate_via_process('perspective_feature_comparison', input_data)
    try:
        if perspective_feature_comparisons_resp.get('other_notes'):
            log_str(f'other_notes: {perspective_feature_comparisons_resp.get("other_notes")}')
        for c in perspective_feature_comparisons_resp["aspect_feature_value_comparison"]:
          feature_name = c.get("feature_name", '')
          if aspect_features.get(feature_name):
              aspect_features[feature_name]['comparison'] = c.get('comparison', 0)
        return with_key(aspect, "aspect_features", list(aspect_features.values()))
    except RuntimeError as e:
        log_str('Unknown error: perspective_feature_comparisons_resp=\n' + dump_json(perspective_feature_comparisons_resp))
        raise e


def calc_aspect_total_score(perspective_aspects):
    return reduce(lambda acc, c: acc + get_float(c, 'aspect_importance_score_to_other_aspects', 0), perspective_aspects, 0)


def with_aspect_comparison(aspect, aspect_total_score):
    aspect_features = aspect['aspect_features']
    aspect_w = get_float(aspect, 'aspect_importance_score_to_other_aspects', 1.0) / aspect_total_score if aspect_total_score > 0 else 1.0
    aspect['normalized_aspect_score'] = aspect_w
    (_, aspect_features2) = with_normalized_value(aspect_features, 'comparison', 'normalized_', 'feature_importance_score_to_other_features', aspect_w)
    aspect['normalized_comparison'] = sum([c['normalized_comparison'] for c in aspect_features2])
    aspect['aspect_features'] = aspect_features2
    return aspect


def with_total_comparison(perspective_aspects):
    # perspective_aspects = perspective_aspects["aspect_features"]
    aspect_total_score = calc_aspect_total_score(perspective_aspects)
    perspective_aspects2 = [with_aspect_comparison(c, aspect_total_score) for c in perspective_aspects]
    comparison_total = sum([c['normalized_comparison'] for c in perspective_aspects2])
    return (comparison_total, perspective_aspects2)


async def calc_superordinate_concept(model, a_concept, b_concept, observer_context_description):
    concepts = f'- {a_concept}\n- {b_concept}'
    context_knowledge_specification = f'### Context description\n{observer_context_description}'
    superordinate_concept_identification_resp = await evaluate_via_process('superordinate_concept_identification', with_model_input_data(
        {
            'concepts': concepts,
            'context_knowledge_specification': context_knowledge_specification
        }, model))
    if superordinate_concept_identification_resp.get('other_notes'):
        log_str(f'other_notes: {superordinate_concept_identification_resp.get("other_notes")}')
    return superordinate_concept_identification_resp['least_common_general_superordinate_concept']


def with_extra_output_specification(input_data: dict, output_content_language: str):
    input_data['_extra_output_specification'] = f'# Extra output specification\nOutput_content_language: {output_content_language}'
    return input_data


async def evaluate(input_data):
    meta = input_data.get('meta', {})
    model = meta.get('model', None)
    (observer_context_description, a_concept, b_concept, frame_of_reference, output_content_language, extra_information_retrieval_strategy) = (
        input_data['observer_context_description'],
        input_data['a_concept'],
        input_data['b_concept'],
        input_data['frame_of_reference'],
        input_data['output_content_language'],
        input_data['extra_information_retrieval_strategy']
    )
    superordinate_concept = await calc_superordinate_concept(model, a_concept, b_concept, observer_context_description)
    (perspective_observer_strategy, point_of_view, perspective_aspects) = await calc_perspective_aspects(model,
                                                                                                         superordinate_concept,
                                                                                                         observer_context_description,
                                                                                                         frame_of_reference,
                                                                                                         output_content_language,
                                                                                                         extra_information_retrieval_strategy)
    perspective_aspects2 = [await with_feature_comparison(c,
                                                          a_concept,
                                                          b_concept,
                                                          model,
                                                          perspective_observer_strategy,
                                                          point_of_view,
                                                          frame_of_reference,
                                                          output_content_language,
                                                          extra_information_retrieval_strategy)
                            for c in perspective_aspects]
    (comparison_total, perspective_aspects3) = with_total_comparison(perspective_aspects2)
    return {
        'superordinate_concept': superordinate_concept,
        'perspective_observer_strategy': perspective_observer_strategy,
        'point_of_view': point_of_view,
        'comparison_total': comparison_total,
        'comparison_winner': a_concept if comparison_total > 0 else (b_concept if comparison_total < 0 else None),
        'perspective_aspects': list(perspective_aspects3)
    }
