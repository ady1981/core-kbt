from common import read_json


def load_process_input(input_id):
    return read_json(f'processes/input/{input_id}.json')