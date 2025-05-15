import json

from ai_function import evaluate
from common import calc_md5, render_template, read_string, read_yaml, parse_json, format_markdown_code
from processes.implementation.common import load_process_input

PROCESS_TYPE = 'estimate_arity2_array_criterial_semantic_equivalence'
PROCESS_VERSION = 1
AI_FUN_NAME = PROCESS_TYPE


def calc_input_id(process_input):
    model = process_input['model'].strip().replace("/", "-").replace(".", "-")
    array_1 = json.dumps(process_input['array_1'])
    array_2 = json.dumps(process_input['array_2'])
    item_json_schema = json.dumps(process_input['item_json_schema'])
    return f'{PROCESS_TYPE}.{PROCESS_VERSION}.{calc_md5(item_json_schema)}.{calc_md5(array_1)}.{calc_md5(array_2)}.{model}'


def calc_instruction(process_input):
    array_1 = process_input['array_1']
    array_2 = process_input['array_2']
    item_json_schema = process_input['item_json_schema']
    data = {'array_1': format_markdown_code('json', json.dumps(array_1, indent=2)),
            'array_2': format_markdown_code('json', json.dumps(array_2, indent=2)),
            'item_json_schema': item_json_schema}
    template_string = read_string(f'ai_functions/{AI_FUN_NAME}/prompt.md.j2')
    return render_template(template_string, data)


async def execute(input_id):
    print(f'start: input_id={input_id}')
    process_input = load_process_input(input_id)
    print('process:\n' + json.dumps(process_input))
    instruction = calc_instruction(process_input)
    model = process_input['model']
    # print('Instruction:\n', instruction) ## TODO
    response_schema = read_yaml(f'ai_functions/{AI_FUN_NAME}/output_schema.yaml')
    response = evaluate(instruction, response_schema, model=model)
    result_state = {'response': response['json'],
                    'model_base_url': response['model_base_url'],
                    'model_name': response['model_name']}
    print(f'end: input_id={input_id}')
    return result_state
