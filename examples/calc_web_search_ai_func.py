import os
from asyncio import run

from dotenv import load_dotenv

import sys
# sys.path.insert(0, '.')

from kbt_core.ai_function import evaluate_function
from kbt_core.common import dump_json, with_model_input_data, write_json

load_dotenv()

AI_FUN_NAME = 'web_search'
OPENAI_MODEL = os.environ["OPENAI_MODEL"]



async def main():
    input_data = {
        'topic_keyword': 'machine learning',
        'qa_query': 'What are applications of machine learning in healthcare?',
        'web_search_limit_n': 2
    }
    r = await evaluate_function(AI_FUN_NAME, with_model_input_data(input_data, OPENAI_MODEL))
    print('=== Response:\n' + dump_json(r))
    formatted_model_name = OPENAI_MODEL.strip().replace('/', '-').replace('.', '-')
    # write_yaml(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.yaml')
    write_json(r, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')


# run(calc_method2())
run(main())