import json

from ai_function import evaluate2
from common import read_string, read_yaml, render_template, format_markdown_code

TEXT = 'Moscow is a Capital City of Russia.'
AI_FUN_NAME = 'estimate_ontology_instances'


def calc_instruction(text):
    template_string = read_string(f'ai_functions/{AI_FUN_NAME}/prompt.md.j2')
    knowledge_base_ontology = read_yaml('elementary/ontology-kb-classes/_all.yaml') + read_yaml('elementary/geography-kb-classes/_all.yaml')
    data = {'knowledge_base_ontology': format_markdown_code('yaml', knowledge_base_ontology),
            'text': text}
    return render_template(template_string, data)


instruction = calc_instruction(TEXT)
print(f'--- instruction:\n{instruction}')
response_schema = read_yaml(f'ai_functions/{AI_FUN_NAME}/output_schema.yaml')
response = evaluate2(instruction, response_schema)
json_response = response['json']
print('=== Response:\n' + json.dumps(json_response, indent=2))
