import asyncio
import copy
import glob
import hashlib
import io
import json
import os
import pathlib
import re
import sys
import time
from functools import reduce
from typing import TypeVar, List, Callable, Any, Coroutine

from jinja2 import Environment
from ruamel.yaml import YAML


def read_string(filepath):
    with open(filepath, 'r') as file:
        return file.read()


def convert_to_dict(subclass_dict):
    return dict(vmap_deep(lambda v: dict(v) if isinstance(v, dict) else v, subclass_dict))


def read_yaml(filepath):
    with open(filepath, 'r') as file:
        yaml = YAML()
        return yaml.load(file)


def read_yamls(filepath):
    """
    Loads multiple YAML documents from a single file using ruamel.yaml.

    Args:
        filepath (str): The path to the YAML file.

    Returns:
        list: A list of dictionaries, where each dictionary represents a YAML document.
              Returns an empty list if the file is empty or contains no valid YAML documents.
    """
    yaml = YAML()
    data = []
    with open(filepath, 'r') as f:
        for doc in yaml.load_all(f):
            if doc is not None:  # Handle empty documents
                data.append(doc)
    return data


def read_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)


def parse_json(json_string):
    return json.loads(json_string)


def write_json(data, filepath, indent=2):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def _write_yaml(yaml_data, filepath):
    yaml = YAML()
    yaml.dump_all(yaml_data, pathlib.Path(filepath))


def write_yaml(data, filepath):
    write_string(dump_yaml(data), filepath)


def write_string(data, filepath):
    with open(filepath, 'w') as file:
        return file.write(data)


def parse_yaml(yaml_string):
    yaml = YAML()
    return dict(yaml.load(yaml_string))


def dump_yaml(data):
    yaml = YAML()
    with io.StringIO() as string_stream:
        yaml.dump(data, string_stream)
        yaml_string = string_stream.getvalue()
    return yaml_string


def dump_json(data, indent=2):
    return json.dumps(data, indent=indent)


def setvalue(adict, key, value):
    adict[key] = value
    return adict


def rename_dict(adict, keys_mapping):
    return reduce(lambda acc, c: setvalue(acc, keys_mapping.get(c, c), adict[c]), adict.keys(), {})


def log_error(str):
  sys.stderr.write(str + '\n')


def calc_md5(value: str) -> str:
    """
    calculates md5 hash of the provided string
    """
    return hashlib.md5(value.encode()).hexdigest()


def list_files(directory, wildcard):
    """Lists files in a directory matching a wildcard pattern using glob.

    Args:
        directory: The directory to search in (string).
        wildcard: The wildcard pattern (string), e.g., "*.txt", "image_*.png".

    Returns:
        A list of strings, where each string is the full path to a matching file.
        Returns an empty list if no files match.
    """
    pattern = os.path.join(directory, wildcard)  # Construct the full path pattern
    files = sorted(glob.glob(pattern))
    return files


def calc_string_with_zeros(number, width):
    return f'{number:0{width}d}'


def render_template(template_string: str, data: dict = None) -> str:
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise TypeError("invalid-data")
    template = Environment().from_string(template_string)
    return template.render(data)


def deep_dict_compare(dict1, dict2):
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict1 == dict2  # Base case: compare non-dict values

    if set(dict1.keys()) != set(dict2.keys()):
        return False

    for key in dict1:
        if not deep_dict_compare(dict1[key], dict2[key]):
            return False

    return True


def traverse(element, leaf_f, path=[], hpath=[]):
    upd_hpath = copy.deepcopy(hpath)
    for child in element.children:
        if child.name:
            traverse(child, leaf_f, path + [child.name], upd_hpath)
            if child.name.startswith('h') and child.text:
                if len(upd_hpath) == 0 or upd_hpath[-1]['name'] != child.name:
                    upd_hpath = upd_hpath + [{'name': child.name, 'text': child.text}]
                else:
                    upd_hpath[-1] = {'name': child.name, 'text': child.text}
        else:
            leaf_f(path, upd_hpath, child)


def n_range(n):
    return range(1, n + 1)


def parse_int(x):
    try:
        return int(x)
    except ValueError:
        return None


def calc_alphanumeric(input_string):
    return re.sub(r'[^a-zA-Z0-9]', '', input_string)


def vmap(f, adict):
    return {k: f(v) for k, v in adict.items()}


def vmap_deep(f, adict):
    return {k: f(vmap_deep(f, v) if isinstance(v, dict) else v) for k, v in adict.items()}


def vfilter(f, adict):
    return reduce(lambda acc, k: with_key(acc, k, adict[k]) if f(k, adict[k]) else acc, adict.keys(), {})


def kvmap(kf, vf, adict):
    return {kf(k, v): vf(k, v) for k, v in adict.items()}


def transform_dict_alphanumerically(adict, key_mapping):
    key_mapping2 = kvmap(lambda k, _v: calc_alphanumeric(k).strip(), lambda _k, v: v, key_mapping)
    return kvmap(lambda k, _v: key_mapping2.get(calc_alphanumeric(k).strip(), k), lambda _k, v: v, adict)


def with_key(adict, k, v):
    adict[k] = v
    return adict


def without_key(adict, k):
    del adict[k]
    return adict


def without_key_safe(adict, k):
    adict2 = copy.deepcopy(adict)
    del adict2[k]
    return adict2


def index_by(index_f, alist):
    return reduce(lambda acc, c: with_key(acc, index_f(c), c), alist, {})


def clear_code_markdown(code):
    r = code.strip()
    r = re.sub(r'^```([^\n]*)?\n', '', r)
    r = re.sub(r'\n```([^\n]*)?$', '', r)
    return r


DOCUMENTATION_BASEDIR = '../../documentation/docs/'


def calc_standard_document_paths2(dir=DOCUMENTATION_BASEDIR):
    paths = list_files(dir, 'Стандарт -*.md')
    for c in list_files(dir, '*'):
        if os.path.isdir(c):
            paths += calc_standard_document_paths2(c)
    return paths


def calc_standard_document_paths():
    return calc_standard_document_paths2()


def clear_initial_block(text, delimiter):
    """
    Removes the initial block of text delimited by a specified delimiter.

    Args:
      text: The input string.
      delimiter: The delimiter string that separates the initial block from the rest of the text. Defaults to "---".

    Returns:
      The input string with the initial block removed, or the original string if the delimiter is not found.
    """
    text = text.strip()
    start_index = text.find(delimiter)
    if start_index == -1:
        return text  # Delimiter not found, return original text

    end_index = text.find(delimiter, start_index + len(delimiter))  # Find the second delimiter
    if end_index == -1:
        return text  # Second delimiter not found, return original text

    remaining_text = text[end_index + len(delimiter):].strip()  # Extract text after the second delimiter and remove leading/trailing whitespace
    return remaining_text


def clear_leading_header(markdown_text):
    r = markdown_text.strip()
    r = re.sub(r'^#([^\n]*)?\n', '', r)
    return r.strip()


def calc_unix_timestamp():
    return int(time.time())


def calc_timestamp():
    return time.time()


T = TypeVar('T')
R = TypeVar('R')


async def async_map(
        f: Callable[[T], Coroutine[Any, Any, R]],
        items: List[T],
        concurrent_n: int = None
) -> List[R]:
    if not items:
        return []

    semaphore = asyncio.Semaphore(concurrent_n) if concurrent_n else None

    async def process(item: T) -> R:
        if semaphore:
            async with semaphore:
                return await f(item)
        return await f(item)

    tasks = [process(item) for item in items]
    return await asyncio.gather(*tasks)


def get_by_path(adict, path_items, default_value=None):
    if len(path_items) == 0:
        return adict
    if len(path_items) == 1:
        return adict.get(path_items[0], default_value)
    else:
        if adict.get(path_items[0], None) is None:
            return default_value
        else:
            return get_by_path(adict[path_items[0]], path_items[1:])


def dict_with(adict, k, v):
    adict[k] = v
    return adict


def with_only_keys(adict, keys):
    return {c: adict[c] for c in keys if c in adict}


def format_markdown_code(lang, code):
    return f'```{lang}\n{code}\n```\n'


def remove_markdown_code(text, lang=''):
    prefix_to_remove = f'```{lang}\n'
    suffix_to_remove = f'```'
    return text.strip().removeprefix(prefix_to_remove).removesuffix(suffix_to_remove)


def log_str(s):
    sys.stderr.write(s + '\n')


def first(arr):
    return arr[0]


def rest(arr):
    return arr[1:]
