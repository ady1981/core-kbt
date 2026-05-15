from functools import reduce

from kbt_core.common import with_model_input_data, index_by, with_key, log_str, async_map, dump_json, get_float, \
    read_string, format_markdown_code, select_item, n_range
from kbt_core.process import execute_process

OUTPUT_CONTENT_LANGUAGE = 'English'
INFORMATION_RETRIEVAL_STRATEGY = 'Use unbiased internal knowledge'
OUTPUT_GENERATION_STRATEGY = '''
Extra_instructions:
- write ONLY existing and correct relations
- write empty relations if no relations
'''


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


async def calc_perspective(model, observer_context_description, frame_of_reference):
    input_data = with_model_input_data({
        'observer_context_description': observer_context_description,
        'frame_of_reference': frame_of_reference,
        '_extra_output_specification': f'# Extra output specification\nOutput_content_language: {OUTPUT_CONTENT_LANGUAGE}'
    }, model)
    response = await evaluate_via_process('full_perspective_identification', input_data)
    return {
        "basis_of_consideration": response["basis_of_consideration"],
        "perspective_observer_strategy": response["perspective_observer_strategy"],
        "point_of_view": response["point_of_view"]
    }


async def calc_perspective_concept_relations2(model, concept_nindex, concept_names, perspective):
    concepts = [f'''
- name: {c}
  kind: entity
  schema: entity_schema
''' for c in concept_names]
    (a_concept, b_concepts) = select_item(concept_nindex - 1, concepts)
    ontology_schema = read_string('elementary/term-elimination-ontology/ontology_schema.yaml')
    meta_ontology = read_string('elementary/term-elimination-ontology/meta_ontology.yaml')
    (basis_of_consideration, perspective_observer_strategy, point_of_view) = (perspective['basis_of_consideration'], perspective['perspective_observer_strategy'], perspective['point_of_view'])
    perspective2 = f'''
### Basis of consideration
{basis_of_consideration}
### Perspective observer strategy
{perspective_observer_strategy}
### point_of_view
{point_of_view}
'''
    input_data = with_model_input_data({
        'a_concept': a_concept,
        'b_concepts': b_concepts,
        'ontology_schema': format_markdown_code('yaml', ontology_schema),
        'meta_ontology': format_markdown_code('yaml', meta_ontology),
        'perspective': perspective2,
        '_information_retrieval_strategy': f'# Information retrieval strategy\n{INFORMATION_RETRIEVAL_STRATEGY}\n',
        '_output_generation_strategy': f'# Output generation strategy\n{OUTPUT_GENERATION_STRATEGY}'
    }, model)
    response = await evaluate_via_process('perspective_concept_relations', input_data)
    print('response:\n', response)
    return response["relation_items"]


async def calc_perspective_concept_relations(model, concept_names, perspective):
    async def calc(index):
        return await calc_perspective_concept_relations2(model, index, concept_names, perspective)
    r = await async_map(calc, n_range(len(concept_names)))
    return [c2 for c in r for c2 in c]


async def evaluate(input_data):
    meta = input_data.get('meta', {})
    model = meta.get('model', None)
    (observer_context_description, frame_of_reference, concepts) = (
        input_data['observer_context_description'],
        input_data['frame_of_reference'],
        input_data['concepts']
    )
    perspective = await calc_perspective(model, observer_context_description, frame_of_reference)
    perspective_concept_relations = calc_perspective_concept_relations(concepts, perspective)
    ## optimization
    ## explain
    result = {}
    return result
