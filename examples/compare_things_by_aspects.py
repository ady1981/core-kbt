import json
import os

from ai_function import evaluate2
from common import read_string, read_yaml, render_template, write_json, dump_yaml

AI_FUN_NAME = 'compare_things_by_aspects'


def calc_instruction():
    template_string = read_string(f'ai_functions/{AI_FUN_NAME}/prompt.md.j2')
    context = 'knowledge representation'
    text_1 = "thesaurus"
    text_2 = "taxonomy"
    aspects = [
      "Primary Purpose",
      "Structural Representation",
      "Organizational Principle",
      "Domain of Application",
      "Nature of Relationships",
      "Information Retrieval"
    ]
    data = {'context': context,
            'text_1': text_1,
            'text_2': text_2,
            'aspects': dump_yaml(aspects)}
    return render_template(template_string, data)


model = os.environ["OPENAI_MODEL"]
formatted_model_name = model.strip().replace("/", "-").replace(".", "-")
instruction = calc_instruction()
print(f'instruction:\n{instruction}')
response_schema = read_yaml(f'ai_functions/{AI_FUN_NAME}/output_schema.yaml')
response = evaluate2(instruction, response_schema, model=model)
json_response = response['json']
print('=== Response:\n' + json.dumps(json_response, indent=2))
write_json(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')
