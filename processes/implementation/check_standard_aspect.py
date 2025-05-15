import json

import items_db
from ai_function import evaluate
from common import read_string, dump_yaml, render_template, calc_md5, read_yaml
from processes.implementation.common import load_process_input

PROCESS_TYPE = 'check_standard_aspect'
AI_FUN_NAME = PROCESS_TYPE
PROCESSING_VERSION = 1


def calc_instruction(standard_name, standard_text, rule_id):
    template_string = read_string(f'ai_functions/{AI_FUN_NAME}/prompt.md.j2')
    rule = items_db.read_item('standard_document_rule', rule_id)
    examples = f"""```yaml
{dump_yaml(rule['examples'])}
```
"""
    counterexamples = f"""```yaml
{dump_yaml(rule['counterexamples'])}
```
"""
    data = {
        'area': '"Информационные технологии"',
        'specified_aspect': rule['specified_aspect'],
        'rule_modality': rule['rule_modality'],
        'examples': examples,
        'counterexamples': counterexamples,
        'standard_name': standard_name,
        'text': standard_text
    }
    return render_template(template_string, data)


def calc_input_id(process_input):
    model = process_input['model'].strip().replace("/", "-").replace(".", "-")
    standard_name = process_input['standard_name']
    standard_text = process_input['standard_text']
    standard_document_rule_id = process_input['standard_document_rule_id']
    return f'{PROCESS_TYPE}.{PROCESSING_VERSION}.{standard_document_rule_id}.{standard_name}.{calc_md5(standard_text)}.{model}'


async def execute(input_id):
    print(f'start: input_id={input_id}')
    process_input = load_process_input(input_id)
    print('process:\n' + json.dumps(process_input))
    standard_document_rule_id = process_input['standard_document_rule_id']
    standard_name = process_input['standard_name']
    standard_text = process_input['standard_text']
    instruction = calc_instruction(standard_name, standard_text, standard_document_rule_id)
    # print('Instruction:\n', instruction)
    response_schema = read_yaml(f'ai_functions/{AI_FUN_NAME}/output_schema.yaml')
    model = process_input['model']
    response = evaluate(instruction, response_schema, model=model)
    if not isinstance(response['json'].get('items'), list):
        raise RuntimeError('invalid-response-schema')
    result_state = {'response': response['json'],
                    'model_base_url': response['model_base_url'],
                    'model_name': response['model_name']}
    print(f'end: input_id={input_id}')
    return result_state
