import json
import os

from ai_function import evaluate2
from common import read_string, read_yaml, render_template, write_json, dump_yaml, escape_yaml_in_markdown, \
    format_markdown_code

AI_FUN_NAME = 'estimate_ontology_LCA'


def calc_instruction():
    template_string = read_string(f'ai_functions/{AI_FUN_NAME}/prompt.md.j2')
    knowledge_base_ontology = read_yaml('elementary/ontology-kb-classes/_all.yaml')
    knowledge_base_ontology = knowledge_base_ontology + read_yaml('elementary/geography-kb-classes/_all.yaml')
    text_1 = 'Moscow'
    text_2 = 'Russia'
    data = {'knowledge_base_ontology': format_markdown_code('yaml', knowledge_base_ontology),
            'texts_context': 'General sense',
            'text_1': text_1,
            'text_2': text_2}
    return render_template(template_string, data)


model = os.environ["OPENAI_MODEL"]
formatted_model_name = model.strip().replace("/", "-").replace(".", "-")
instruction = calc_instruction()
print(f'instruction:\n{instruction}')
response_schema = read_yaml(f'ai_functions/{AI_FUN_NAME}/output_schema.yaml')
response = evaluate2(instruction, response_schema, model=model)
json_response = response['json']
print('=== Response:\n' + json.dumps(json_response, indent=2))
write_json(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')
