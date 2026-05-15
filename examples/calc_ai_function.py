import json
import os
from asyncio import run

from dotenv import load_dotenv

from ai_function import evaluate_function
from kbt_core.ai_function_impl import concept_set_covering
from common import dump_json, with_model_input_data, write_json

load_dotenv()

AI_FUN_NAME = 'concept_aspect_comparison'
OPENAI_MODEL = os.environ["OPENAI_MODEL"]


async def calc_method1():
    observer_context_description = 'Рассматриваются живые организмы в биологической систематике.'
    frame_of_reference = 'Unbiased framework' ## 'Common sense'
    print(dump_json(await concept_set_covering.calc_perspective(observer_context_description, frame_of_reference)))


async def calc_method2():
    concept_names = ['Human', 'Plants', 'Animals']
    perspective = {
        "basis_of_consideration": "Living organisms within biological systematics (taxonomy, phylogeny, morphology, physiology, ecology, etc.)",
        "perspective_observer_strategy": "Objective analysis of biological entities based on established scientific principles and empirical evidence, minimizing anthropocentric or subjective bias.",
        "point_of_view": "Scientific/Systematic biological perspective, focusing on classification, relationships, and functional roles of organisms."
    }
    print(dump_json(await concept_set_covering.calc_perspective_concept_relations(None, concept_names, perspective)))


async def main():
    observer_context_description = 'Рассматриваются живые организмы в биологической систематике.'
    frame_of_reference = 'Unbiased framework' ## 'Common sense'

    frame_of_reference = 'Unbiased framework' ## 'Common sense'
    output_content_language = 'Russian'
    extra_information_retrieval_strategy = 'Only_unbiased_authorative_sources: true'
    input_data = {
        'observer_context_description': observer_context_description,
        'frame_of_reference': frame_of_reference,
        ## TODO
    }
    r = await evaluate_function(AI_FUN_NAME, with_model_input_data(input_data, OPENAI_MODEL))
    print('=== Response:\n' + dump_json(r))
    formatted_model_name = OPENAI_MODEL.strip().replace('/', '-').replace('.', '-')
    # write_yaml(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.yaml')
    write_json(r, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')


run(calc_method2())