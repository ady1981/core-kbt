import json
import os
import sys

from ai_function_template import evaluate2
from common import read_string, read_yaml, render_template, write_json

AI_FUN_NAME = 'list_best_tasks_for_llm_effectivess'


def calc_instruction():
    template_string = read_string(f'ai_function_templates/{AI_FUN_NAME}/prompt.md.j2')
    data = {'context': 'Informational Technology',
            'tasks_range': '3-12',
            'task_area': 'software development'}
    return render_template(template_string, data)


def main():
    if __name__ == '__main__':
        if len(sys.argv) >= 2:
            model = sys.argv[1].strip()
        else:
            raise RuntimeError('invalid-model')
        formatted_model_name = model.strip().replace("/", "-").replace(".", "-")
        instruction = calc_instruction()
        print(f'Instruction:\n{instruction}')
        response_schema = read_yaml(f'ai_function_templates/{AI_FUN_NAME}/output_schema.yaml')
        response = evaluate2(instruction, response_schema, model=model)['json']
        print('Response:\n' + json.dumps(response, indent=2))
        write_json(response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')


main()