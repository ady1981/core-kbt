import importlib


async def evaluate_function(f_name, input_data):
    module = importlib.import_module(f'function_impl.{f_name}')
    function_to_call = getattr(module, 'evaluate')
    return await function_to_call(input_data)
