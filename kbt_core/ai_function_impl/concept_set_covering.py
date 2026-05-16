from kbt_core.common import with_model_input_data, index_by, log_str, async_map, dump_json, read_string, \
    format_markdown_code, select_item, n_range, vmap, list_intersection, with_only_keys
from kbt_core.process import execute_process
from minimal_set_covering import calc_set_covering

OUTPUT_CONTENT_LANGUAGE = 'English'
INFORMATION_RETRIEVAL_STRATEGY = 'Use unbiased internal knowledge'
OUTPUT_GENERATION_STRATEGY = '''
Extra_instructions:
- write ONLY existing and correct relations for ONLY specified entities
- write empty relations if no correct relations
'''
ISMEMBER_RELATIONS = ['subclassOf_schema', 'instanceOf_schema', 'partOf_schema']


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
### Point of view
{point_of_view}
'''
    input_data = with_model_input_data({
        'a_concept': format_markdown_code('yaml', a_concept),
        'b_concepts': format_markdown_code('yaml', ''.join(b_concepts)),
        'ontology_schema': format_markdown_code('yaml', ontology_schema),
        'meta_ontology': format_markdown_code('yaml', meta_ontology),
        'perspective': perspective2,
        '_information_retrieval_strategy': f'# Information retrieval strategy\n{INFORMATION_RETRIEVAL_STRATEGY}\n',
        '_output_generation_strategy': f'# Output generation strategy\n{OUTPUT_GENERATION_STRATEGY}',
        '_extra_output_specification': f'# Extra output specification\nOutput_content_language: {OUTPUT_CONTENT_LANGUAGE}'
    }, model)
    response = await evaluate_via_process('perspective_concept_relations', input_data)
    try:
        return [relation for relation in response["relation_items"] if relation.get('is_correct')]
    except KeyError as e:
        log_str('key-error:\n response=' + dump_json(response))
        raise e


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
            subject_entities = relation['domain']
            if isinstance(subject_entities, str):
                subject_entities = [subject_entities]
            if isinstance(relation['range'], str):
                relation['range'] = [relation['range']]
            if concept in subject_entities:
                for object in relation['range']:
                    by_object = by_subject.get(object, [])
                    by_object.append(relation)
                    by_subject[object] = by_object
                    result[concept] = by_subject
    result = vmap(lambda by_object: vmap(lambda relations: index_by(lambda relation: relation.get("schema"), relations), by_object), result)
    return result


def is_member_of(leftside_concept, rightside_concept, concept_relations_map):
    return list_intersection(concept_relations_map
                          .get(leftside_concept, {})
                          .get(rightside_concept, {})
                          .keys(),
                          ISMEMBER_RELATIONS)


def is_same(leftside_concept, rightside_concept, concept_relations_map):
    ## - allow any "sameAs"
    ## - consider mutual partOf relation as "sameAs"
    return ("sameIdentityAs_schema" in concept_relations_map.get(leftside_concept, {}).get(rightside_concept, {}).keys()) or \
             ("sameIdentityAs_schema" in concept_relations_map.get(rightside_concept, {}).get(leftside_concept, {}).keys()) or \
             ("partOf_schema" in concept_relations_map.get(leftside_concept, {}).get(rightside_concept, {}).keys() and \
              "partOf_schema" in concept_relations_map.get(rightside_concept, {}).get(leftside_concept, {}).keys())


def calc_concept_set_covering(concepts, concept_relations_map):
    concepts_n = len(concepts)
    member_element_sets = [[subject_concept_idx
                            for subject_concept_idx in n_range(concepts_n)
                            if set_idx == subject_concept_idx or \
                               is_same(concepts[subject_concept_idx - 1], concepts[set_idx - 1], concept_relations_map) or \
                               is_member_of(concepts[subject_concept_idx - 1], concepts[set_idx - 1], concept_relations_map)]
                           for set_idx in n_range(concepts_n)]
    # print('member_element_sets:\n' + dump_json(member_element_sets)) ## TODO
    set_covering_ids = calc_set_covering(concepts_n, member_element_sets)
    eliminated_ids = [idx for idx in n_range(concepts_n) if not idx in set_covering_ids]
    return (set_covering_ids, eliminated_ids)


def ensure_concept_relations_nonsymmetry(concepts, concept_relations_map):
    for c1 in concepts:
        for c2 in concepts:
            if c1 != c2:
                if is_member_of(c1, c2, concept_relations_map) and is_member_of(c2, c1, concept_relations_map) \
                        and not is_same(c1, c2, concept_relations_map):
                    truncated_concept_relations_map = with_only_keys(concept_relations_map, [c1, c2])
                    log_str(f'invalid-concept_relations-symmetry: c1={c1}, c2={c2}, truncated_concept_relations_map=\n' + dump_json(truncated_concept_relations_map))
                    raise RuntimeError('invalid-concept_relations-symmetry')


async def evaluate(input_data):
    try:
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
        ## ensure consistency
        ensure_concept_relations_nonsymmetry(concepts, concept_relations_map)
        ## optimization
        (set_covering_ids, eliminated_ids) = calc_concept_set_covering(concepts, concept_relations_map)
        ## result
        result = {
            'covering_concepts': [{
                'concept': concepts[c - 1],
                'by_range_relations': concept_relations_map.get(concepts[c - 1], {})
            } for c in set_covering_ids],
            'eliminated_concepts': [{
                'concept': concepts[c - 1],
                'by_range_relations': concept_relations_map[concepts[c - 1]]
            } for c in eliminated_ids]
        }
        return result
    except RuntimeError as e:
        if str(e) == 'invalid-concept_relations-symmetry':
            return {'error': 'invalid-concept-relations-symmetry'}
        else:
            log_str(f'unknown-error: input_id={input_data.get("input_id")}')
            raise e
