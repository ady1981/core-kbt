import json
import os
import sys
import traceback
from openai import OpenAI
from dotenv import load_dotenv

from common import deep_dict_compare, clear_code_markdown, read_string, render_template, read_yaml, log_str, dump_json

load_dotenv()

client = OpenAI()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("OPENAI_MODEL")
DEFAULT_TIMEOUT = float(os.getenv("DEFAULT_TIMEOUT", "300.0"))
MAX_LOGGING_LEN = int(os.getenv('MAX_LOGGING_LEN', '1000'))


def evaluate2(instruction, response_schema, model=MODEL, temperature=0, **chat_completions_args):
    prompt = instruction + f'''
# RESPONSE FORMAT
Respond only in JSON format strictly using the provided JSON Schema specification for your response: 
```
{json.dumps(response_schema)}
```
'''
    response = client.chat.completions.create(
        **chat_completions_args,
        model=model,
        temperature=temperature,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={
            "type": "json_object"
        },
        timeout=DEFAULT_TIMEOUT
    )

    raw_answer = response.choices[0].message.content
    answer2 = {}
    try:
        answer = json.loads(clear_code_markdown(raw_answer))
        if deep_dict_compare(answer, response_schema):
            answer2 = {'json': None}
        else:
            if isinstance(answer, dict) and ("array" == answer.get('type', '')) and isinstance(answer.get('items'), list):
                answer2 = {'json': answer['items']}
            elif answer.get('properties', False):
                answer2 = {'json': answer['properties']}
            else:
                answer2 = {'json': answer}
    except RuntimeError:
        sys.stderr.write('cannot-evaluate => return as raw:\n')
        sys.stderr.write(traceback.format_exc() + '\n')
        answer2 = {'raw': raw_answer}
    finally:
        answer2['model_base_url'] = OPENAI_BASE_URL
        answer2['model_name'] = model
        return answer2


def calc_module_name(func_name):
    return f'ai_function_templates/{func_name}'


def evaluate(func_name, input_data):
    #input_data2 = json.dumps(input_data, indent=2)
    #log_str(
    #     f'--- evaluate: {func_name}\n{input_data2[0:MAX_LOGGING_LEN] + " ..."}\n')
    meta = input_data.get('meta', {})
    template_string = read_string(f'{calc_module_name(func_name)}/prompt.md.j2')
    instruction = render_template(template_string, input_data)
    log_str(f'--- instruction meta: {json.dumps(meta)}\n')
    log_str(f'--- instruction:\n{instruction[0:MAX_LOGGING_LEN] + " ..."}\n')
    response_schema = read_yaml(f'{calc_module_name(func_name)}/output_schema.yaml')
    response = evaluate2(instruction, response_schema, **meta)
    if response.get('json'):
        return response['json']
    else:
        log_str(f'--- invalid response:\n' + dump_json(response))
        raise RuntimeError('invalid response')

