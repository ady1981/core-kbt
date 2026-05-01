import os

from common import read_json

MODEL = os.environ['OPENAI_MODEL']


def load_process_input(input_id):
    return read_json(f'processes/input/{input_id}.json')


def calc_model(process_input):
    return process_input.get('meta', {}).get('model', MODEL)