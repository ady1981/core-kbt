import json
import os
import sys
from asyncio import run
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'kbt_core'))

import ai_function_template
from ai_function import evaluate_function
from ai_function_impl.concept_set_covering import calc_concept_set_covering
from kbt_core.ai_function_impl import concept_set_covering
from common import dump_json, with_model_input_data, write_json

load_dotenv()

AI_FUN_NAME = 'factual_question_answering'
OPENAI_MODEL = os.environ["OPENAI_MODEL"]


async def main():
    question = 'What is weather in Moscow today?'
    input_data = {
        'meta': {'mcp': 'exa_web_search'},
        'question': question,
        'context_knowledge_specification': 'Weather',
        '_extra_information_retrieval_strategy': '## Strategy\nSearch the data on the Internet.',
        '_output_generation_strategy': '# Generation strategy\n1. Don\'t use predictions.\n2. Use only verifiable facts.'
    }
    r = await ai_function_template.async_evaluate(AI_FUN_NAME, input_data)
    print('=== Response:\n' + dump_json(r))
    formatted_model_name = OPENAI_MODEL.strip().replace('/', '-').replace('.', '-')
    # write_yaml(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.yaml')
    write_json(r, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')


# run(calc_method2())
run(main())