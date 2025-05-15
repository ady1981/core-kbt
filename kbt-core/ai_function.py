import json
import os
import sys
import traceback
from openai import OpenAI

from common import deep_dict_compare, clear_code_markdown

client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")


def evaluate(instruction, response_schema, model=MODEL):
    prompt = instruction + f'''
## RESPONSE FORMAT
Respond only in JSON format strictly using the provided JSON Schema specification for your response: 
```json
{json.dumps(response_schema)}
```
'''
    # print(f'Prompt:\n{prompt}') ## TODO: remove
    response = client.chat.completions.create(
        model=model,
        temperature=0,
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
    # print(f'Response:\n{raw_answer}')
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
