import json

from ai_function_template import evaluate2
from common import read_string, render_template, calc_md5, read_yaml, log_str
from .common import load_process_input, calc_model

PROCESS_TYPE = 'superordinate_concept_identification_af'
PROCESS_VERSION = 1
AI_FUN_NAME = 'superordinate_concept_identification'


def calc_instruction(process_input):
    template_string = read_string(f'ai_function_templates/{AI_FUN_NAME}/prompt.md.j2')
    return render_template(template_string, process_input)


def calc_input_id(process_input: dict):
    model = calc_model(process_input)
    model_hash = calc_md5(model)
    instruction = calc_instruction(process_input)
    instruction_hash = calc_md5(instruction)
    return f'{PROCESS_TYPE}.{PROCESS_VERSION}.{model_hash}.{instruction_hash}'


async def execute(input_id):
    process_input = load_process_input(input_id)
    log_str(f'start: input_id={input_id}')
    log_str('process:\n' + json.dumps(process_input))
    response_schema = read_yaml(f'ai_function_templates/{AI_FUN_NAME}/output_schema.yaml')
    response = evaluate2(calc_instruction(process_input), response_schema, model=calc_model(process_input))
    json_response = response['json']
    log_str(f'end: input_id={input_id}')
    return {'response': json_response}
