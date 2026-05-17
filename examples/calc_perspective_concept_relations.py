import json
import os

from ai_function_template import evaluate2
from common import read_string, read_yaml, render_template, write_json, format_markdown_code

AI_FUN_NAME = 'perspective_concept_relations'


def calc_instruction():
    a_concept = '''
- name: Human
  kind: entity
  schema: entity_schema
'''
    b_concepts = '''
- name: Plants
  kind: entity
  schema: entity_schema
- name: Animals
  kind: entity
  schema: entity_schema
'''
    ontology_schema = read_string('elementary/term-elimination-ontology/ontology_schema.yaml')
    meta_ontology = read_string('elementary/term-elimination-ontology/meta_ontology.yaml')
    perspective = 'Scientific biological perspective, focusing on classification, relationships, and functional roles of organisms.'
    information_retrieval_strategy = 'Use unbiased internal knowledge'
    output_generation_strategy = '''
Extra_instructions:  
- write ONLY existing and correct relations
- write empty relations if no relations
'''
    data = {
        'a_concept': a_concept,
        'b_concepts': b_concepts,
        'ontology_schema': format_markdown_code('yaml', ontology_schema),
        'meta_ontology': format_markdown_code('yaml', meta_ontology),
        'perspective': perspective,
        '_information_retrieval_strategy': f'# Information retrieval strategy\n{information_retrieval_strategy}\n',
        '_output_generation_strategy': f'# Output generation strategy\n{output_generation_strategy}'
    }
    template_string = read_string(f'ai_function_templates/{AI_FUN_NAME}/prompt.md.j2')
    return render_template(template_string, data)


def main():
    model = os.environ["OPENAI_MODEL"]
    formatted_model_name = model.strip().replace("/", "-").replace(".", "-")
    instruction = calc_instruction()
    print(f'instruction:\n{instruction}')
    response_schema = read_yaml(f'ai_function_templates/{AI_FUN_NAME}/output_schema.yaml')
    response = evaluate2(instruction, response_schema, model=model)
    try:
        json_response = response['json']
        print('=== Response:\n' + json.dumps(json_response, indent=2, ensure_ascii=False))
        # write_yaml(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.yaml')
        write_json(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')
    except KeyError as e:
        print('Unknown Error:\n', response)
        raise e

main()