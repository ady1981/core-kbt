import json

from processes.implementation.common import load_process_input

PROCESS_TYPE = 'test'
PROCESS_VERSION = 1


def calc_input_id(process_input):
    test_value = process_input['test']
    return f'{PROCESS_TYPE}.{PROCESS_VERSION}.{test_value}'


async def execute(input_id):
    process_input = load_process_input(input_id)
    # process_input = {} ## TODO
    print(f'start: input_id={input_id}')
    print('process:\n' + json.dumps(process_input))
    print(f'end: input_id={input_id}')
    return {'result': 1}
