import json
import os
import sys
from asyncio import run

from ai_function import evaluate_function
from ai_function_template import evaluate2
from common import read_string, read_yaml, render_template, write_json, read_json, dump_json, log_str
from json_schema_extension import calc_prompt_target_json_schema

AIM_AI_FUN_NAME = 'list_best_tasks_for_llm_effectivess'
CONTEXT = 'information technology'
TASKS_RANGE = '3-10'
# TASK_AREA = 'software development'
TASK_AREA = 'symbolic reasoning'


def evaluate_aim_ai_function(model):
    formatted_model_name = model.strip().replace("/", "-").replace(".", "-")
    template_string = read_string(f'ai_function_templates/{AIM_AI_FUN_NAME}/prompt.md.j2')
    data = {'context': CONTEXT,
            'tasks_range': TASKS_RANGE,
            'task_area': TASK_AREA}
    instruction = render_template(template_string, data)
    log_str(f'Instruction:\n{instruction}')
    response_schema = read_yaml(f'ai_function_templates/{AIM_AI_FUN_NAME}/output_schema.yaml')
    response = evaluate2(instruction, response_schema, model=model)['json']
    write_json(response, f'temp/{AIM_AI_FUN_NAME}.{formatted_model_name}.response.json')
    return response


def extract_arrays(model_results):
    return [[c2['task category'] for c2 in c['tasks']] for c in model_results ]


async def merge_semantically_lists_into_list(model, arrays, array_item_json_schema):
    merge_strategy = {'not_comparable': 'merge', 'comparable_not_equal': 'merge'}
    updated_array = await evaluate_function('merge_items_by_semantics', {'meta': {'model': model}, 'array_item_json_schema': array_item_json_schema, 'arrays': arrays, 'merge_strategy': merge_strategy})
    return updated_array


def split_and_merge_items(model, updated_array):
    ai_fun_name = 'split_and_merge_items'
    template_string = read_string(f'ai_function_templates/{ai_fun_name}/prompt.md.j2')
    data = {'context': CONTEXT,
            'list_of_items': updated_array}
    instruction = render_template(template_string, data)
    formatted_model_name = model.strip().replace("/", "-").replace(".", "-")
    log_str(f'instruction:\n{instruction}')
    response_schema = read_yaml(f'ai_function_templates/{ai_fun_name}/output_schema.yaml')
    response = evaluate2(instruction, response_schema, model=model)
    json_response = response['json']
    log_str('=== Response:\n' + json.dumps(json_response, indent=2))
    write_json(json_response, f'temp/{ai_fun_name}.{formatted_model_name}.response.json')
    return json_response


async def main():
    if __name__ == '__main__':
        if len(sys.argv) >= 2:
            models = sys.argv[1].strip().split(';')
            if len(models) <= 1:
                raise RuntimeError('invalid-models-count')
        else:
            raise RuntimeError('invalid-models')

        model_results = [evaluate_aim_ai_function(c) for c in models]
        # model_results = [read_json(f'temp/{c}') for c in ['list_best_tasks_for_llm_effectivess.deepseek-deepseek-chat.response.json', 'list_best_tasks_for_llm_effectivess.google-gemini-2-0-flash.response.json']]
        arrays = extract_arrays(model_results)
        array_item_json_schema = calc_prompt_target_json_schema(read_yaml(f'ai_function_templates/{AIM_AI_FUN_NAME}/output_schema.yaml')['properties']['tasks'])
        log_str(f'arrays: {arrays}')
        log_str(f'array_item_json_schema: {array_item_json_schema}')
        updated_array = await merge_semantically_lists_into_list(models[0], arrays, array_item_json_schema)
        log_str(f'updated_array: {updated_array}')
        ## updated_array: ['Code Review and Bug Detection', 'Code Explanation and Documentation', 'Code Generation', 'Debugging', 'Documentation Generation and Updates', 'Code Generation', 'Code Refactoring', 'Test Case Generation', 'Code Translation (Transpilation)']
        updated_array2 = split_and_merge_items(models[0], updated_array)
        write_json(updated_array2, f'temp/merged_list_best_tasks_for_llm_effectivess.json')
        result = updated_array2['final_rebuilt_list']
        print(result)


run(main())
