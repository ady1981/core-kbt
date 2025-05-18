import json
import os

from ai_function import evaluate
from common import read_string, read_yaml, render_template, write_json

AI_FUN_NAME = 'list_best_tasks_for_llm_effectivess'


def calc_instruction():
    template_string = read_string(f'ai_functions/{AI_FUN_NAME}/prompt.md.j2')
    data = {'context_topic': 'Informational Technology',
            'tasks_range': '3-5',
            'task_area': 'SRE'}
    return render_template(template_string, data)


model = os.environ["OPENAI_MODEL"]
formatted_model_name = model.strip().replace("/", "-").replace(".", "-")
instruction = calc_instruction()
print(f'Instruction:\n{instruction}')
response_schema = read_yaml(f'ai_functions/{AI_FUN_NAME}/output_schema.yaml')
response = evaluate(instruction, response_schema, model=model)['json']
print('Response:\n' + json.dumps(response, indent=2))
write_json(response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')