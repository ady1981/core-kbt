import json
import os

from ai_function_template import evaluate2
from common import read_string, read_yaml, render_template, write_json, dump_yaml

AI_FUN_NAME = 'abstractive_summarize'


def calc_instruction():
    template_string = read_string(f'ai_function_templates/{AI_FUN_NAME}/prompt.md.j2')
    content_topic = 'Ideas'
    summarizing_strategy = '''
* The summary should be abstract and express the most valued hint.
* It should be no longer than 1 sentence
* Split complex sentence into list items.
'''
    content = '''
* Seamless, context-aware integration with AI assistants for code generation, refactoring, and debugging.
* Highly performant, low-latency language server protocol (LSP) implementation offering instant feedback and deep semantic understanding.
* Built-in, zero-configuration support for reproducible environments (e.g., containers or declarative dependency management).
'''
    language = 'English'
    examples = '''
## Summarizing strategy
...
## Content domain
Innovative ideas
## Content
...
## Response
```yaml
summary: |
  The next-generation development platform must integrate seamless:
    * AI assistance
    * ultra-fast semantic understanding via LSP
    * zero-configuration support for reproducible environments.
```
'''
    data = {'content_topic': content_topic,
            'summarizing_strategy': summarizing_strategy,
            'examples': examples,
            'language': language,
            'content': content}
    return render_template(template_string, data)


model = os.environ["OPENAI_MODEL"]
formatted_model_name = model.strip().replace("/", "-").replace(".", "-")
instruction = calc_instruction()
print(f'instruction:\n{instruction}')
response_schema = read_yaml(f'ai_function_templates/{AI_FUN_NAME}/output_schema.yaml')
response = evaluate2(instruction, response_schema, model=model)
json_response = response['json']
print('=== Response:\n' + json.dumps(json_response, indent=2))
write_json(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')
