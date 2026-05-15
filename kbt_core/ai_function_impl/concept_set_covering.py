from kbt_core.common import with_model_input_data, index_by, log_str, async_map, dump_json, read_string, format_markdown_code, select_item, n_range, vmap, list_intersection
from kbt_core.process import execute_process
from minimal_set_covering import calc_set_covering

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
    return response["relation_items"]


async def calc_perspective_concept_relations(model, concepts, perspective):
    async def calc(index):
        return await calc_perspective_concept_relations2(model, index, concepts, perspective)
    r = await async_map(calc, n_range(len(concepts)))
    return [c2 for c in r for c2 in c]


def calc_concept_relations_map(concepts, perspective_concept_relations):
    result = {}
    for concept in concepts:
        by_subject = result.get(concept, {})
        for relation in perspective_concept_relations:
            subject_entities = relation['subjectEntities']
            if isinstance(subject_entities, str):
                subject_entities = [subject_entities]
            if isinstance(relation['objectEntities'], str):
                relation['objectEntities'] = [relation['objectEntities']]
            if concept in subject_entities:
                for object in relation['objectEntities']:
                    by_object = by_subject.get(object, [])
                    by_object.append(relation)
                    by_subject[object] = by_object
                    result[concept] = by_subject
    result = vmap(lambda by_object: vmap(lambda relations: index_by(lambda relation: relation.get("schema"), relations), by_object), result)
    return result


def calc_concept_set_covering(concepts, concept_relations_map):
    concepts_n = len(concepts)
    is_member_relations = ['subclassOf_schema', 'instanceOf_schema', 'partOf_schema']
    member_element_sets = [[subject_concept_idx
                            for subject_concept_idx in n_range(concepts_n)
                              if subject_concept_idx == set_idx or
                                list_intersection(concept_relations_map
                                              .get(concepts[subject_concept_idx - 1], {})
                                              .get(concepts[set_idx - 1], {})
                                              .keys(),
                                              is_member_relations)]
                           for set_idx in n_range(concepts_n)]
    print('member_element_sets:\n' + dump_json(member_element_sets)) ## TODO
    set_covering_ids = calc_set_covering(concepts_n, member_element_sets)
    eliminated_ids = [idx for idx in n_range(concepts_n) if not idx in set_covering_ids]
    return (set_covering_ids, eliminated_ids)


async def evaluate(input_data):
    meta = input_data.get('meta', {})
    model = meta.get('model', None)
    (observer_context_description, frame_of_reference, concepts) = (
        input_data['observer_context_description'],
        input_data['frame_of_reference'],
        input_data['concepts']
    )
    perspective = await calc_perspective(model, observer_context_description, frame_of_reference)
    perspective_concept_relations = await calc_perspective_concept_relations(model, concepts, perspective)
    concept_relations_map = calc_concept_relations_map(concepts, perspective_concept_relations)
    ## optimization
    (set_covering_ids, eliminated_ids) = calc_concept_set_covering(concepts, concept_relations_map)
    ## result
    result = {
        'covering_concepts': [concepts[c - 1] for c in set_covering_ids],
        'eliminated_concepts': [{
            'concept': concepts[c - 1],
            'by_object_relations': concept_relations_map[concepts[c - 1]]
        } for c in eliminated_ids]
    }
    return result
