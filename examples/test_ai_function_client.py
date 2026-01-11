import json
import os

import requests

from common import parse_yaml, read_yaml, format_markdown_code, read_string, write_json, dump_yaml, write_yaml

AI_SERVER_BASE_URL = os.getenv('AI_SERVER_BASE_URL', 'http://127.0.0.1:5000')
API_TOKEN = os.getenv('AI_FUNC_API_TOKEN')


def eval_ai_func(func_name, input_data):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Api-Token': API_TOKEN
        }
        response = requests.put(f"{AI_SERVER_BASE_URL}/ai-func/{func_name}", headers=headers, json=input_data)
        response.raise_for_status()
        if response.text and response.headers.get('Content-Type', '').startswith('application/json'):
            return {'json': response.json()}
        elif response.text:
            return {'raw': response.text}

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Something went wrong: {err}")
    return None


# result = eval_ai_func('generate_what_is', {
#     'context': 'Geography',
#     'attribute': 'capital (in a shortest form)',
#     'description': 'of Russia'
# })

# left = ["codeGeneration","conversationalAgent","informationExtraction","textSummarization","languageTranslation","questionAnswering","textGeneration","textClassification"]
# right = ["TextRewritingTask","LanguageTranslationTask","InformationExtractionTask","TextClassificationTask","TextGenerationTask","SummarizationTask"]
# array_item_json_schema = parse_yaml('''
# type: array
# items:
#   - type: string
#     description: a task type for LLM
# ''')
# merge_strategy = {'not_comparable': 'merge', 'comparable_not_equal': 'merge'}
# result = eval_ai_func('merge_items_by_semantics',
#                       {'array_item_json_schema': array_item_json_schema, 'arrays': [left, right], 'merge_strategy': merge_strategy})

AI_FUN_NAME = 'formalize_generative_task'
summarization_task = read_yaml('elementary/generative-tasks/abstractive_summarization.yaml')
examples = format_markdown_code('yaml', dump_yaml({'elementary_tasks': [summarization_task]}))
result = eval_ai_func(AI_FUN_NAME, {
    'task': 'Objective critical review writing',
    'examples': examples
})['json']['result']

print(json.dumps(result, indent=2))
write_yaml(result, f'temp/{AI_FUN_NAME}.response.yaml')
