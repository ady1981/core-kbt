import json
import os

from ai_function import evaluate
from common import read_string, read_yaml, render_template, write_json, format_markdown_code

AI_FUN_NAME = 'estimate_llm_tasks_ontology_classes'


def calc_instruction():
    template_string = read_string(f'ai_functions/{AI_FUN_NAME}/prompt.md.j2')
    data = {'knowledge_base_ontology': format_markdown_code('yaml', read_string('elementary/ontology-kb-classes/_all.yaml'))}
    return render_template(template_string, data)


model = os.environ["OPENAI_MODEL"]
instruction = calc_instruction()
print(f'instruction:\n{instruction}')
response_schema = read_yaml(f'ai_functions/{AI_FUN_NAME}/output_schema.yaml')
response = evaluate(instruction, response_schema, model=model)
json_response = response['json']
print('=== Response:\n' + json.dumps(json_response, indent=2))
write_json(json_response, f'temp/{AI_FUN_NAME}.{model.strip().replace("/", "-").replace(".", "-")}.response.json')
