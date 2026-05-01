import asyncio
import json
import os

import process
from ai_function_template import evaluate2
from common import read_string, read_yaml, render_template, write_json, dump_yaml, format_markdown_code, write_yaml, \
    async_map

AI_FUN_NAME = 'perspective_feature_comparison'


def calc_instruction():
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
    data = {
        'a_concept': a_concept,
        'b_concept': b_concept,
        'aspect_name': aspect_name,
        'aspect_features': aspect_features,
        'frame_of_reference': frame_of_reference,
        'perspective_observer_strategy': perspective_observer_strategy,
        'point_of_view': point_of_view
    }
    template_string = read_string(f'ai_function_templates/{AI_FUN_NAME}/prompt.md.j2')
    return render_template(template_string, data)


async def main():
    model = os.environ['OPENAI_MODEL']
    formatted_model_name = model.strip().replace('/', '-').replace('.', '-')
    instruction = calc_instruction()
    print(f'instruction:\n{instruction}')
    response_schema = read_yaml(f'ai_function_templates/{AI_FUN_NAME}/output_schema.yaml')
    ##
    process_inputs = [{}]
    process_results = await async_map(process.execute_process, process_inputs)
    ##
    response = evaluate2(instruction, response_schema, model=model)
    json_response = response['json']
    print('=== Response:\n' + json.dumps(json_response, indent=2))
    # write_yaml(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.yaml')
    write_json(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')

asyncio.run(main())