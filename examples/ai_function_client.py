import json
import os

import requests

import ai_function
from common import read_yaml

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


# response = requests.put(f"{AI_SERVER_BASE_URL}/state/list-ai-functions", headers={'Api-Token': API_TOKEN, 'accept': 'application/json'})
# response.raise_for_status()
# print(json.dumps(response.json(), indent=2))


# print(json.dumps(eval_ai_func('generate_what_is', {
#     'context': 'Geography',
#     'attribute': 'capital (in a shortest form)',
#     'description': 'of Russia'
# })['json'], indent=2))

# print(json.dumps(eval_ai_func('generate_which_is', {
#     'meta': {'model': 'deepseek-chat'},
#     'context': 'LLM prompting',
#     'attribute': 'better prompt beginning for LLM',
#     'options': '''
# 1. `In a context of "{{context}}".`
# 2. `In a field of "{{field}}".`
# '''
# })['json'], indent=2))

result = ai_function.evaluate('rewrite_thing_by_examples', {
    'context': 'Task types for LLM', 
    'item': 'TextRewritingTask',
    'examples': ['codeGeneration', 'conversationalAgent', 'questionAnswering']
})
print(json.dumps(result, indent=2))
