import json
import os

from ai_function import evaluate
from common import read_string, read_yaml, render_template, write_json, dump_yaml

AI_FUN_NAME = 'estimate_ontology_instances'


def calc_instruction():
    template_string = read_string(f'ai_functions/{AI_FUN_NAME}/prompt.md.j2')
    knowledge_base_ontology = read_yaml('elementary/ontology-kb-classes/_all.yaml')
    knowledge_base_ontology = knowledge_base_ontology + read_yaml('elementary/geography-kb-classes/_all.yaml')
    knowledge_base_ontology_str = f'''```yaml
{dump_yaml(knowledge_base_ontology)}
```    
'''
    text = 'Moscow is a Capital City of Russia.'
    data = {'knowledge_base_ontology': knowledge_base_ontology_str,
            'text': text}
    return render_template(template_string, data)


model = os.environ["OPENAI_MODEL"]
formatted_model_name = model.strip().replace("/", "-").replace(".", "-")
instruction = calc_instruction()
print(f'instruction:\n{instruction}')
response_schema = read_yaml(f'ai_functions/{AI_FUN_NAME}/output_schema.yaml')
response = evaluate(instruction, response_schema, model=model)
json_response = response['json']
print('=== Response:\n' + json.dumps(json_response, indent=2))
write_json(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')
