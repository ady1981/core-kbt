import json

import items_db
from ai_function import evaluate
from common import read_string, render_template, read_yaml, calc_md5
from processes.implementation.common import load_process_input

PROCESS_TYPE = 'extract_terms2'
PROCESSING_VERSION = 1

def is_document_passage_body_type_of_input(process_input):
    return process_input.get('standard_document_passage_area', False) and process_input.get('standard_document_passage_body', False)


def calc_input_id(process_input):
    if is_document_passage_body_type_of_input(process_input):
        standard_document_passage = process_input['standard_document_passage_body']
    else:
        standard_document_passage_id = str(process_input['standard_document_passage_id']).strip()
        standard_document_passage = items_db.read_item('standard_document_passage', standard_document_passage_id)['body']
    standard_document_passage_hash = calc_md5(standard_document_passage)
    term_definition_id = str(process_input['term_definition_id']).strip()
    model = process_input['model'].strip().replace("/", "-").replace(".", "-")
    return f'{PROCESS_TYPE}_{PROCESSING_VERSION}.{standard_document_passage_hash}.{term_definition_id}.{model}'


# {{area}}
# {{definition_of_terms}}
# {{text}}

async def execute(input_id):
    print(f'start: input_id={input_id}')
    process_input = load_process_input(input_id)
    print('process:\n' + json.dumps(process_input))
    standard_document_passage_id = process_input.get('standard_document_passage_id')
    term_definition_id = process_input['term_definition_id']
    model = process_input['model']
    definition_of_terms = items_db.read_item('term_definition', term_definition_id)['definition']
    if is_document_passage_body_type_of_input(process_input):
        area = process_input['standard_document_passage_area']
        text = process_input['standard_document_passage_body']
    else:
        standard_document_passage = items_db.read_item('standard_document_passage', standard_document_passage_id)
        area = standard_document_passage['area']
        text = standard_document_passage['body']
    template_string = read_string('ai_functions/extract_terms/prompt.md.j2')
    instruction = render_template(template_string, {'area': area, 'definition_of_terms': definition_of_terms, 'text': text})
    response_schema = read_yaml('ai_functions/extract_terms/output_schema.yaml')
    response = evaluate(instruction, response_schema, model)
    result_state = {'response': response['json'], 'model_base_url': response['model_base_url'], 'model_name': response['model_name']}
    print(f'end: input_id={input_id}')
    return result_state
