import json
import os

from ai_function_template import evaluate2
from common import read_string, read_yaml, render_template, write_json

AI_FUN_NAME = 'full_perspective_identification'


def calc_instruction():
    observer_context_description = 'Рассматриваются живые организмы в биологической систематике.'
    frame_of_reference = 'Unbiased framework' ## 'Common sense'
    output_content_language = 'English'
    # sources_strategy = 'Only_unbiased_authorative_sources: true'
    data = {
        'observer_context_description': observer_context_description,
        'frame_of_reference': frame_of_reference,
        # '_information_retrieval_strategy': f'## Sources strategy/n{sources_strategy}'
        '_extra_output_specification': f'# Extra output specification\nOutput_content_language: {output_content_language}'
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
    print('=== Response:\n' + json.dumps(json_response, indent=2, ensure_ascii=False))
    # write_yaml(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.yaml')
    write_json(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')

main()