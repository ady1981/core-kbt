import json
import os

from ai_function_template import evaluate2
from common import read_string, read_yaml, render_template, write_json, dump_yaml, format_markdown_code, write_yaml

AI_FUN_NAME = 'perspective_features'


def calc_instruction():
    concept = 'Programming language'
    observer_context_description = 'We need a programming language for microprocessors'
    frame_of_reference = 'Common sense'
    data = {
        'concept': concept,
        'observer_context_description': observer_context_description,
        'frame_of_reference': frame_of_reference,
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
    json_response = response['json']
    print('=== Response:\n' + json.dumps(json_response, indent=2))
    # write_yaml(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.yaml')
    write_json(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')

main()