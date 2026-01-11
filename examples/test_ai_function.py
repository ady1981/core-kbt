import json
import os

from ai_function_template import evaluate2
from common import read_string, read_yaml, render_template, write_json, dump_yaml, format_markdown_code, write_yaml

AI_FUN_NAME = 'aspect_based_devergence_analysis'


def calc_instruction():
    # items_topic = 'Logic'
    # left_item = 'Aspect'
    # right_item = 'Feature'
    items_topic = 'Cars'
    left_item = 'Haval Dargo'
    right_item = 'Haval Jolion'


    analysis_strategy = '# Analysis strategy\nGranularity: Fine-grained\n'
    data = {
        '_extra_output_specification': None,
        '_analysis_strategy': analysis_strategy,
        '_examples': None,
        'items_topic': items_topic,
        'left_item': left_item,
        'right_item': right_item
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