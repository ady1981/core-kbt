import importlib


def calc_process_module(process_type):
    return f'process_impl.{process_type}'


def calc_module_function(process_type, function_name, args):
    module = importlib.import_module(calc_process_module(process_type))
    function_to_call = getattr(module, function_name)
    return function_to_call(args)


print(calc_module_function('test', 'calc_input_id', {'test_value': 1}))