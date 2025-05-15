import json

from ai_function import evaluate
from common import read_string, read_yaml, render_template, write_json

AI_FUN_NAME = 'estimate_term_aspects'


def calc_instruction():
    template_string = read_string(f'ai_functions/{AI_FUN_NAME}/prompt.md.j2')
    context = 'Programming'
    term = 'Programming Language'
    data = {'context': context,
            'term': term}
    return render_template(template_string, data)


instruction = calc_instruction()
print(f'instruction:\n{instruction}')
response_schema = read_yaml(f'ai_functions/{AI_FUN_NAME}/output_schema.yaml')
response = evaluate(instruction, response_schema)
json_response = response['json']
print('Response:\n' + json.dumps(json_response, indent=2))
write_json(response, f'temp/estimate_term_aspects_response.json')
