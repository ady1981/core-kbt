import asyncio
import json
import os

import process
from common import write_json, async_map

AI_FUN_NAME = 'perspective_feature_comparison'


async def execute_process():
    a_concept = 'C++ (Programming language)'
    b_concept = 'Assembler (Programming language)'
    aspect_name = 'Hardware Interfacing'
    aspect_features = '''
- Direct Register Access
- Interrupt Handling Support
- Concurrency Model
'''
    frame_of_reference = 'Common sense'
    perspective_observer_strategy = 'Evaluation'
    point_of_view = 'Practical Requirements'
    process_input = {
        'process_type': 'perspective_feature_comparison_af',
        'a_concept': a_concept,
        'b_concept': b_concept,
        'aspect_name': aspect_name,
        'aspect_features': aspect_features,
        'frame_of_reference': frame_of_reference,
        'perspective_observer_strategy': perspective_observer_strategy,
        'point_of_view': point_of_view
    }
    process_inputs = [process_input]
    process_results = await async_map(process.execute_process, process_inputs)
    return process_results[0]['state']['response']


async def main():
    model = os.environ['OPENAI_MODEL']
    formatted_model_name = model.strip().replace('/', '-').replace('.', '-')
    response = await execute_process()
    print('=== Response:\n' + json.dumps(response, indent=2))
    # write_yaml(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.yaml')
    write_json(response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')

asyncio.run(main())