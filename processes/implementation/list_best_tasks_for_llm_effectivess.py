import json

from ai_function import evaluate
from common import calc_md5, render_template, read_string, read_yaml
from processes.implementation.common import load_process_input

PROCESS_TYPE = 'list_best_tasks_for_llm_effectivess'
PROCESS_VERSION = 1
AI_FUN_NAME = PROCESS_TYPE


def calc_input_id(process_input):
    model = process_input['model'].strip().replace("/", "-").replace(".", "-")
    input_hash = calc_md5(''.join([
        calc_md5(process_input['context_topic']),
        calc_md5(process_input['tasks_range']),
        calc_md5(process_input['task_area'])
    ]))
    return f'{PROCESS_TYPE}.{PROCESS_VERSION}.{input_hash}.{model}'


def calc_instruction(process_input):
    context_topic = process_input['context_topic']
    tasks_range = process_input['tasks_range']
    task_area = process_input['task_area']
    data = {
        'context_topic': context_topic,
        'tasks_range': tasks_range,
        'task_area': task_area
    }
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
