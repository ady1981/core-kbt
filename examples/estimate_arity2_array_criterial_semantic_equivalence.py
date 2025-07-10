import json
import os

from ai_function import evaluate2
from common import read_string, read_yaml, render_template, write_json, dump_yaml, format_markdown_code, read_json, \
    parse_yaml, write_yaml

AI_FUN_NAME = 'estimate_arity2_array_criterial_semantic_equivalence'


def with_only_task_name(tasks):
    return [{'task name': c['task name']} for c in tasks]


def calc_instruction():
    template_string = read_string(f'ai_functions/{AI_FUN_NAME}/prompt.md.j2')
    array_1 = ["codeGeneration","conversationalAgent","informationExtraction","textSummarization","languageTranslation","questionAnswering","textGeneration","textClassification"]
    array_2 = ["TextRewritingTask","LanguageTranslationTask","InformationExtractionTask","TextClassificationTask","TextGenerationTask","SummarizationTask"]
    item_json_schema = parse_yaml('''
type: array
items:
  - type: string
    description: a task type for LLM
''')
    data = {'array_1': format_markdown_code('json', json.dumps(array_1, indent=2)),
            'array_2': format_markdown_code('json', json.dumps(array_2, indent=2)),
            'item_json_schema': item_json_schema}
    return render_template(template_string, data)


model = os.environ["OPENAI_MODEL"]
formatted_model_name = model.strip().replace("/", "-").replace(".", "-")
instruction = calc_instruction()
print(f'instruction:\n{instruction}')
response_schema = read_yaml(f'ai_functions/{AI_FUN_NAME}/output_schema.yaml')
response = evaluate2(instruction, response_schema, model=model)
json_response = response['json']
print('=== Response:\n' + json.dumps(json_response, indent=2))
write_yaml(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.yaml')
