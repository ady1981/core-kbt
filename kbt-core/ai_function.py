import json
import os
import sys
import traceback

from openai import OpenAI

from common import deep_dict_compare, clear_code_markdown

client = OpenAI()
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("OPENAI_MODEL")


def evaluate(instruction, response_schema, model=MODEL, temperature=0, **chat_completions_args):
    prompt = instruction + f'''
# RESPONSE FORMAT
Respond only in JSON format strictly using the provided JSON Schema specification for your response: 
```json
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
        }
    )

    raw_answer = response.choices[0].message.content
    answer2 = {}
    try:
        answer = json.loads(clear_code_markdown(raw_answer))
        if deep_dict_compare(answer, response_schema):
            answer2 = {'json': None}
        else:
            if isinstance(answer, dict) and ("array" == answer.get('type', '')) and isinstance(answer.get('items'), list):
                answer2 = {'json': answer.get('items')}
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
