from common import convert_to_dict, parse_yaml, remove_markdown_code, vfilter, with_key


def is_item_semantic_representation(description):
    extra_meta = convert_to_dict(parse_yaml(remove_markdown_code(description, lang='yaml')))
    return extra_meta.get('semantic_type') == 'item_semantic_representation'


def calc_semantic_schema(array_json_schema):
    semantic_properties = vfilter(lambda _k, v:
                                  is_item_semantic_representation(v.get('description')) if (v.get('description') is not None) else False,
                                  array_json_schema['properties'])
    upd_required_properties = list(semantic_properties.keys())
    return {
        'type': 'array',
        'properties': semantic_properties,
        'required': upd_required_properties
    }
