from asyncio import run
from dotenv import load_dotenv

from common import encode_term, calc_md5, write_yaml, dump_json, async_map, log_str
from knowledge_helper import calc_perspective
from process import execute_process

load_dotenv()


async def evaluate_via_process(process_type, input_data):
    process_input = input_data
    process_input['process_type'] = process_type
    process_inputs = [process_input]
    process_results = await async_map(execute_process, process_inputs)
    try:
        return process_results[0]['state']['response']
    except KeyError as e:
        log_str(f'Error: process_results:\n' + dump_json(process_results))
        raise e


async def main():
    input_data = {
        'aspect': 'Fuel efficiency',
        'aspect_feature': 'Fuel consumption',
        'superordinate_concept': 'evolute i-space',
        'a_concept': encode_term('evolute i-space 4x4'),
        'b_concept': encode_term('evolute i-space'),
        # 'perspective': calc_perspective('Unbiased objective comparison', 'Based on car characteristics', 'Customer selecting car with maximum range per tank', 3)
    }
    response = await evaluate_via_process('webcite_better_verify', input_data)
    print('=== Response:\n' + dump_json(response))
    hash = calc_md5(response['other_notes'])
    write_yaml(response, f'temp/webcite3.{hash}.response.yaml')

run(main())