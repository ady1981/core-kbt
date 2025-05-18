import json
import os

from ai_function import evaluate
from common import read_string, read_yaml, render_template, write_json, dump_yaml, format_markdown_code, read_json

AI_FUN_NAME = 'estimate_arity2_array_criterial_semantic_equivalence'


def with_only_task_name(tasks):
    return [{'task name': c['task name']} for c in tasks]


def calc_instruction():
    template_string = read_string(f'ai_functions/{AI_FUN_NAME}/prompt.md.j2')
    array_1 = with_only_task_name(read_json('temp/list_best_tasks_for_llm_effectivess.deepseek-deepseek-chat.response.json')['tasks'])
    array_2 = with_only_task_name(read_json('temp/list_best_tasks_for_llm_effectivess.google-gemini-2-0-flash.response.json')['tasks'])
    item_json_schema = read_yaml('examples/estimate_arity2_array_criterial_semantic_equivalence_items_schema.yaml')
    data = {'array_1': format_markdown_code('json', json.dumps(array_1, indent=2)),
            'array_2': format_markdown_code('json', json.dumps(array_2, indent=2)),
            'item_json_schema': item_json_schema}
    return render_template(template_string, data)


model = os.environ["OPENAI_MODEL"]
formatted_model_name = model.strip().replace("/", "-").replace(".", "-")
instruction = calc_instruction()
print(f'instruction:\n{instruction}')
response_schema = read_yaml(f'ai_functions/{AI_FUN_NAME}/output_schema.yaml')
response = evaluate(instruction, response_schema, model=model)
json_response = response['json']
print('Response:\n' + json.dumps(json_response, indent=2))
write_json(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')
