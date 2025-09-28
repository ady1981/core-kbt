import json
import os

from ai_function_template import evaluate2
from common import read_string, read_yaml, render_template, write_json, dump_yaml

AI_FUN_NAME = 'split_and_merge_items'


def calc_instruction():
    template_string = read_string(f'ai_function_templates/{AI_FUN_NAME}/prompt.md.j2')
    context = 'information technology'
    list_of_items = ['Debugging and Error Resolution', 'Code Refactoring & Optimization', 'Code Debugging and Explanation', 'Code Refactoring', 'Code Explanation & Comprehension']
    data = {'context': context,
            'list_of_items': list_of_items}
    return render_template(template_string, data)


model = os.environ["OPENAI_MODEL"]
formatted_model_name = model.strip().replace("/", "-").replace(".", "-")
instruction = calc_instruction()
print(f'instruction:\n{instruction}')
response_schema = read_yaml(f'ai_function_templates/{AI_FUN_NAME}/output_schema.yaml')
response = evaluate2(instruction, response_schema, model=model)
json_response = response['json']
print('=== Response:\n' + json.dumps(json_response, indent=2))
write_json(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')
