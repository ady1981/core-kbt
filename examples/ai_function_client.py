import json
import os

import requests

AI_SERVER_BASE_URL = os.getenv('AI_SERVER_BASE_URL', 'http://127.0.0.1:5000')


def eval_ai_func(func_name, input_data):
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
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


# print(json.dumps(eval_ai_func('generate_what_is', {
#     'context': 'Geography',
#     'qualifier': 'capital (in a shortest form)',
#     'description': 'of Russia'
# })['json'], indent=2))

print(json.dumps(eval_ai_func('generate_which_is', {
    'context': 'LLM prompting',
    'qualifier': 'better prompt beginning for LLM',
    'options': '''
1. `In a context of "{{context}}".`
2. `In a field of "{{field}}".`
'''
})['json'], indent=2))
