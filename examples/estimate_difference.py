import json
import os

from ai_function_template import evaluate2
from common import read_string, read_yaml, render_template, write_json

AI_FUN_NAME = 'estimate_difference'


def calc_instruction():
    template_string = read_string(f'ai_function_templates/{AI_FUN_NAME}/prompt.md.j2')
    data = {
        'context': '"general sense"',
        'thing_1': 'milk',
        'thing_2': 'kefir'
    }
    return render_template(template_string, data)


def main():
    model = "google/gemini-2.0-flash"
    # model = "deepseek/deepseek-chat"
    formatted_model_name = model.strip().replace("/", "-").replace(".", "-")
    instruction = calc_instruction()
    print(f'instruction:\n{instruction}')
    response_schema = read_yaml(f'ai_function_templates/{AI_FUN_NAME}/output_schema.yaml')
    response = evaluate2(instruction, response_schema, model=model)
    json_response = response['json']
    print('=== Response:\n' + json.dumps(json_response, indent=2))
    write_json(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')

main()