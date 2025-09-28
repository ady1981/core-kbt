from common import convert_to_dict, parse_yaml, remove_markdown_code, vfilter, get_first_key


def is_prompt_target_item(description):
    if description is not None:
        extra_meta = convert_to_dict(parse_yaml(remove_markdown_code(description, lang='yaml')))
        return extra_meta.get('is_prompt_target', False)
    else:
        return False


def calc_prompt_target_json_schema(array_json_schema):
    prompt_target_properties = vfilter(lambda _k, v:
                                  is_prompt_target_item(v.get('description')) if (v.get('description') is not None) else False,
                                  dict(array_json_schema['items']['properties']))
    return {
        'type': 'array',
        'items': {
            'type': 'string',
            'description': get_first_key(prompt_target_properties)
        }
    }
