import copy
import importlib
import os
import traceback

from common import write_json, log_error, read_json, list_files, async_map

STATUSES = ['initial', 'running', 'error', 'terminated']


def calc_module_input_id(process_type, process_input):
    module = importlib.import_module(calc_process_module(process_type))
    function_to_call = getattr(module, 'calc_input_id')
    return function_to_call(process_input)


def create_process(process_input):
    process_type = process_input['process_type']
    process_input2 = copy.deepcopy(process_input)
    process_input_id = calc_module_input_id(process_type, process_input2)
    process_input2['input_id'] = process_input_id
    if not already_existed_process(process_input_id):
        write_json(process_input2, f'processes/input/{process_input_id}.json')
        write_json({}, f'processes/by_status/initial/{process_input_id}.json')
        return process_input_id
    else:
        raise RuntimeError('process-already-exists')




def calc_process_module(process_type):
    return f'processes.implementation.{process_type}'


def already_existed_process(input_id):
    return any(os.path.exists(f'processes/by_status/{c}/{input_id}.json') for c in STATUSES)


def calc_input_directory_name():
    return f'processes/input'


def calc_state_directory_name(status):
    return f'processes/by_status/{status}'


def calc_state_file_name(status, input_id):
    return f'processes/by_status/{status}/{input_id}.json'


def read_ids(status):
    return [c.removesuffix('.json') for c in os.listdir(calc_state_directory_name(status))]


def read_input(input_id):
    return read_json(f'{calc_input_directory_name()}/{input_id}.json')


def read_state(input_id, status=None):
    if status is not None:
        return with_status(read_json(f'{calc_state_directory_name(status)}/{input_id}.json'), status)
    else:
        status = read_status(input_id)
        return with_status(read_json(f'{calc_state_directory_name(status)}/{input_id}.json'), status)


def read_status(input_id):
    for c in reversed(STATUSES):
        path = f'{calc_state_directory_name(c)}/{input_id}.json'
        if os.path.exists(path):
            return c
    raise RuntimeError('process-not-found')


def with_status(state, status):
    state['status'] = status
    return state


def update_status(input_id, upd_status, upd_state=None):
    if len(input_id.strip()) == 0:
        raise RuntimeError('invalid-input-id')
    state = read_state(input_id)
    status = state['status']
    if upd_state is not None:
        upd_state2 = with_status(upd_state, upd_status)
    else:
        upd_state2 = with_status(state, upd_status)
    write_json(upd_state2, calc_state_file_name(upd_status, input_id))
    os.remove(calc_state_file_name(status, input_id))
    return upd_state2


def update_state(input_id, status, upd_state):
    state_filename = calc_state_file_name(status, input_id)
    if os.path.exists(state_filename):
        write_json(upd_state, state_filename)
    else:
        raise RuntimeError('invalid-process-status')


def calc_input_id(process_filepath):
    return process_filepath.split('/')[-1].removesuffix('.json')


def read_process_input(input_id):
    return read_json(f'{calc_input_directory_name()}/{input_id}.json')


def list_terminated_process_files(filepath_wildcard):
    return list_files('processes/by_status/terminated', filepath_wildcard)


def _calc_input_id(process_type, input):
    module = importlib.import_module(calc_process_module(process_type))
    function_to_call = getattr(module, 'calc_input_id')
    return function_to_call(input)


async def _execute_process(process_type, input_id):
    try:
        update_status(input_id, 'running')
        module = importlib.import_module(calc_process_module(process_type))
        function_to_call = getattr(module, 'execute')
        result_state = await function_to_call(input_id)
        return update_status(input_id, 'terminated', result_state)
    except Exception as exception:
        log_error(f'error-in-process: input_id={input_id}')
        traceback.print_exc()  ## TODO: write to std error
        error_state = read_state(input_id, 'running')
        error_state['error'] = str(exception)
        return update_status(input_id, 'error', error_state)


async def execute_process(process_input):
    process_type = process_input['process_type']
    process_input_id = _calc_input_id(process_type, process_input)
    process_input['input_id'] = process_input_id
    try:
        create_process(process_input)
    except RuntimeError as e:
        if str(e) != 'process-already-exists':
            raise e
    state = read_state(process_input_id)
    if state['status'] in ['terminated', 'error']:
        result = {'input': process_input, 'state': state}
    elif state['status'] == 'running':
        log_error(f'already-running-process: input_id={process_input_id}')
        raise RuntimeError('already-running-process')
    else:
        upd_state = await _execute_process(process_type, process_input_id)
        result = {'input': process_input, 'state': upd_state}
    return result
