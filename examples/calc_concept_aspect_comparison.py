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
    observer_context_description = 'Работаю фрилансером-дизайнером, много времени провожу в Adobe Photoshop и Lightroom на мобильном, часто редактирую фото/видео на ходу, синхронизирую с MacBook, важна стабильность ПО и автономность батареи (день без подзарядки), бюджет до 120 000 руб.'
    a_concept = 'Google Pixel 8 Pro'
    b_concept = 'iPhone 15 Pro'

    frame_of_reference = 'Unbiased framework' ## 'Common sense'
    output_content_language = 'Russian'
    extra_information_retrieval_strategy = 'Only_unbiased_authorative_sources: true'
    input_data = {
        'observer_context_description': observer_context_description,
        'frame_of_reference': frame_of_reference,
        'a_concept': a_concept,
        'b_concept': b_concept,
        'output_content_language': output_content_language,
        'extra_information_retrieval_strategy': extra_information_retrieval_strategy
    }
    r = await evaluate_function(AI_FUN_NAME, with_model_input_data(input_data, OPENAI_MODEL))
    print('=== Response:\n' + dump_json(r))
    formatted_model_name = OPENAI_MODEL.strip().replace('/', '-').replace('.', '-')
    # write_yaml(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.yaml')
    write_json(r, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')


run(main())