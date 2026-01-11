import json
import os

from ai_function_template import evaluate2
from common import read_string, read_yaml, render_template, write_json, dump_yaml, format_markdown_code, write_yaml

AI_FUN_NAME = 'formalize_generative_task'


def calc_instruction():
    summarization_task = read_yaml('elementary/generative-tasks/abstractive_summarization.yaml')
    examples = format_markdown_code('yaml', dump_yaml({'elementary_tasks': [summarization_task]}))
    data = {
      'task': 'aspect_based_devergence_analysis',
      'examples': examples
    }
    template_string = read_string(f'ai_function_templates/{AI_FUN_NAME}/prompt.md.j2')
    return render_template(template_string, data)


model = os.environ["OPENAI_MODEL"]
formatted_model_name = model.strip().replace("/", "-").replace(".", "-")
instruction = calc_instruction()
print(f'instruction:\n{instruction}')
response_schema = read_yaml(f'ai_function_templates/{AI_FUN_NAME}/output_schema.yaml')
response = evaluate2(instruction, response_schema, model=model)
json_response = response['json']
print('=== Response:\n' + json.dumps(json_response, indent=2))
write_yaml(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.yaml')
