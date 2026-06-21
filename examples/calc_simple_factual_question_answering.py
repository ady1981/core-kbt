import json
import os
from asyncio import run

from dotenv import load_dotenv

import ai_function_template
from ai_function import evaluate_function
from ai_function_impl.concept_set_covering import calc_concept_set_covering
from kbt_core.ai_function_impl import concept_set_covering
from common import dump_json, with_model_input_data, write_json

load_dotenv()

AI_FUN_NAME = 'factual_question_answering'
OPENAI_MODEL = os.environ["OPENAI_MODEL"]


async def main():
    question = 'The current time in Moscow'
    input_data = {
        'question': question,
        'context_knowledge_specification': 'Only authoritative sources'
    }
    r = await ai_function_template.async_evaluate(AI_FUN_NAME, input_data)
    print('=== Response:\n' + dump_json(r))
    formatted_model_name = OPENAI_MODEL.strip().replace('/', '-').replace('.', '-')
    # write_yaml(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.yaml')
    write_json(r, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')


# run(calc_method2())
run(main())