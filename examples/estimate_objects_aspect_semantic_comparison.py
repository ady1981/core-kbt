import json

from ai_function import evaluate
from common import read_string, read_yaml, render_template, write_json, dump_yaml

AI_FUN_NAME = 'estimate_objects_aspect_semantic_comparison'


def calc_instruction():
    template_string = read_string(f'ai_functions/{AI_FUN_NAME}/prompt.md.j2')
    context = 'Programming'
    text_1 = 'Python'
    text_2 = 'Node.js'
    aspects = [
      "Type System",
      "Memory Management",
      "Concurrency Model",
      "Control Flow Structures",
      "Evaluation Strategy",
      "Exception Handling",
      "Modularity and Encapsulation",
      "Polymorphism",
      "Inheritance",
      "Metaprogramming"
    ]
    data = {'context': context,
            'text_1': text_1,
            'text_2': text_2,
            'aspects': dump_yaml(aspects)}
    return render_template(template_string, data)


instruction = calc_instruction()
print(f'instruction:\n{instruction}')
response_schema = read_yaml(f'ai_functions/{AI_FUN_NAME}/output_schema.yaml')
response = evaluate(instruction, response_schema)
json_response = response['json']
print('Response:\n' + json.dumps(json_response, indent=2))
write_json(response, f'temp/estimate_objects_aspect_semantic_comparison_response.json')
