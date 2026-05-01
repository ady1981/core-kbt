import json
import os
from asyncio import run

from dotenv import load_dotenv

from ai_function import evaluate_function
from common import dump_json, with_model_input_data, write_json

load_dotenv()

AI_FUN_NAME = 'concept_aspect_comparison'
OPENAI_MODEL = os.environ["OPENAI_MODEL"]


async def main():
    observer_context_description = 'We need a programming language for a hardware driver'
    frame_of_reference = 'Unbiased framework' ## 'Common sense'
    a_concept = 'Java'
    b_concept = 'C++'
    output_content_language = 'English'
    input_data = {
        'observer_context_description': observer_context_description,
        'frame_of_reference': frame_of_reference,
        'a_concept': a_concept,
        'b_concept': b_concept,
        'output_content_language': output_content_language
    }
    r = await evaluate_function(AI_FUN_NAME, with_model_input_data(input_data, OPENAI_MODEL))
    print('=== Response:\n' + dump_json(r))
    formatted_model_name = OPENAI_MODEL.strip().replace('/', '-').replace('.', '-')
    # write_yaml(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.yaml')
    write_json(r, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')


run(main())