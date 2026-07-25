import os
from asyncio import run

import load_dotenv

from common import dump_json, with_model_input_data, write_json

load_dotenv()

AI_FUN_NAME = 'web_search'
OPENAI_MODEL = os.environ["OPENAI_MODEL"]



async def main():
    input_data = {
    }
    r = await evaluate_function(AI_FUN_NAME, with_model_input_data(input_data, OPENAI_MODEL))
    print('=== Response:\n' + dump_json(r))
    formatted_model_name = OPENAI_MODEL.strip().replace('/', '-').replace('.', '-')
    # write_yaml(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.yaml')
    write_json(r, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')


# run(calc_method2())
run(main())