import json
import os

from common import log_str, calc_md5, calc_simple_md5
from webcite_helper import better_verify
from .common import load_process_input

PROCESS_TYPE = 'webcite_verify'
PROCESS_VERSION = 1


def calc_input_id(process_input):
    hash_v = calc_simple_md5([process_input.get(c, '').strip() for c in ['aspect', 'aspect_feature', 'superordinate_concept', 'a_concept', 'b_concept', 'perspective']])
    return f'{PROCESS_TYPE}.{PROCESS_VERSION}.{hash_v}'


async def execute(input_id):
    process_input = load_process_input(input_id)
    log_str(f'start: input_id={input_id}')
    log_str('process:\n' + json.dumps(process_input))
    webcite_api_key = os.environ['WEBCITE_API_KEY']
    aspect = process_input['aspect']
    aspect_feature = process_input['aspect_feature']
    superordinate_concept = process_input['superordinate_concept']
    a_concept = process_input['a_concept']
    b_concept = process_input['b_concept']
    perspective = process_input.get('perspective')
    result = better_verify(webcite_api_key, a_concept, b_concept, superordinate_concept, aspect, aspect_feature, perspective)
    log_str(f'end: input_id={input_id}')
    return {'response': result}
