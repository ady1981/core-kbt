import json
import os

from ai_function_template import evaluate2
from common import read_string, read_yaml, render_template, write_json, dump_yaml, format_markdown_code, write_yaml

AI_FUN_NAME = 'ontology_validation'


def calc_instruction():
    ontology_schema = format_markdown_code('yaml', read_string('elementary/meta-ontology/ontology_schema.yaml'))
    ontology = format_markdown_code('yaml', read_string('elementary/meta-ontology/core_ontology.yaml'))
    knowledge_domain = 'common sense'
    data = {
        'ontology_schema': ontology_schema,
        'ontology': ontology,
        'context_knowledge_specification':  f'### Knowledge domain\n{knowledge_domain}',
        '_output_generation_strategy': '# Output generation strategy\n'
                                       '- Consider the Ontology schema as schema and the ontology as data to apply the schema'

    }
    template_string = read_string(f'ai_function_templates/{AI_FUN_NAME}/prompt.md.j2')
    return render_template(template_string, data)


def main():
    model = os.environ["OPENAI_MODEL"]
    formatted_model_name = model.strip().replace("/", "-").replace(".", "-")
    instruction = calc_instruction()
    print(f'instruction:\n{instruction}')
    response_schema = read_yaml(f'ai_function_templates/{AI_FUN_NAME}/output_schema.yaml')
    response = evaluate2(instruction, response_schema, model=model)
    json_response = response['json']
    print('=== Response:\n' + json.dumps(json_response, indent=2))
    # write_yaml(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.yaml')
    write_json(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')

main()