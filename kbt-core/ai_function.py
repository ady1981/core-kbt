import importlib

from common import read_string
import ai_function_template

PY_IMPL_FUN_TYPE = 'py_implementation'
J2_FUN_TYPE = 'j2_template'


def calc_module_name(func_name):
    return f'ai_function_impl.{func_name}'


async def evaluate_function(func_name, input_data):
    module = importlib.import_module(calc_module_name(func_name))
    function_to_call = getattr(module, 'evaluate')
    return await function_to_call(input_data)


def calc_function_type(func_name):
    try:
        module = importlib.import_module(calc_module_name(func_name))
        if getattr(module, 'evaluate') is not None:
            return PY_IMPL_FUN_TYPE
    except ModuleNotFoundError:
        try:
            if read_string(f'{ai_function_template.calc_module_name(func_name)}/prompt.md.j2') is not None:
                return J2_FUN_TYPE
        except FileNotFoundError:
            return None
