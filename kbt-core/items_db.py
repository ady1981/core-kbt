from common import read_yaml, list_files, calc_string_with_zeros, read_string, parse_int, write_yaml, _write_yaml

ID_WIDTH = 4

def calc_item_directory(name):
    return f'elementary/{name}'


def calc_item_filepath(name, id):
    return f'{calc_item_directory(name)}/{calc_string_with_zeros(int(id), ID_WIDTH)}.yaml'


def read_item(name, id):
    if isinstance(id, int):
        id2 = id
    else:
        id2 = int(id)
    formatted_id = calc_string_with_zeros(id2, ID_WIDTH)
    item_filepath = calc_item_filepath(name, id)
    item = read_yaml(item_filepath)
    for c in list_files(calc_item_directory(name), f'{formatted_id}.*.*'):
        filename_parts = (c.split('/')[-1]).split('.')
        fieldname = filename_parts[-2]
        item[fieldname] = read_string(f'{c}')
    return item


def read_items(name):
    return [read_item(name, calc_id(c)) for c in list_files(calc_item_directory(name), '*.yaml')]


def calc_id(filepath):
    return parse_int((filepath.split('/')[-1]).split('.')[0])


def find_last_id(name):
    ids = [calc_id(c) for c in list_files(calc_item_directory(name), '*.yaml')]
    ids = [c for c in ids if c is not None]
    if len(ids) == 0:
        return 0
    else:
        return max(ids)


def insert_item(name, item):
    last_id = find_last_id(name)
    item['id'] = last_id + 1
    return write_item(name, item)


def write_item(name, item): ##TODO: remove as legacy
    return update_item(name, item)


def update_item(name, item):
    if item.get('id', False):
        filename = calc_item_filepath(name, item['id'])
        write_yaml(item, filename)
        return item
    else:
        raise Exception('item-does-not-exist')
