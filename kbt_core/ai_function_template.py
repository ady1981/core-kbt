import json
import os
import re
import sys
import traceback
from typing import Any, Dict

import openai
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from openai import OpenAI, AsyncOpenAI

from kbt_core.common import deep_dict_compare, clear_code_markdown, read_string, render_template, read_yaml, log_str, \
    dump_json, read_json, calc_md5, create_trimmed_dict, calc_json_hash

load_dotenv()

MCP_SERVERS = read_json(os.getenv('MCP_SERVERS_CONFIG_FILE'))
OPENAI_TOOLS_MODEL = os.getenv('OPENAI_TOOLS_MODEL')
MESSAGES_LIMIT = int(os.getenv('MESSAGES_LIMIT', '20'))

client = OpenAI()
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')
MODEL = os.getenv('OPENAI_MODEL')
DEFAULT_TIMEOUT = float(os.getenv('DEFAULT_TIMEOUT', '300.0'))
MAX_LOGGING_LEN = int(os.getenv('MAX_LOGGING_LEN', '1000'))


def calc_prompt(instruction, response_schema):
    return instruction + f'''
# RESPONSE FORMAT
Respond only in JSON format strictly using the provided JSON Schema specification for your response: 
```
{json.dumps(response_schema)}
```
'''


def simple_chat_completion2(instruction, response_schema, model=MODEL, temperature=0, **chat_completions_args):
    prompt = calc_prompt(instruction, response_schema)
    response = client.chat.completions.create(
        **chat_completions_args,
        model=model,
        temperature=temperature,
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ],
        response_format={
            'type': 'json_object'
        },
        timeout=DEFAULT_TIMEOUT
    )
    raw_answer = response.choices[0].message.content
    return raw_answer


def simple_chat_completion(instruction, response_schema, model=MODEL, temperature=0, **chat_completions_args):
    raw_answer = simple_chat_completion2(instruction, response_schema, model=model, temperature=temperature, **chat_completions_args)
    answer2 = {}
    try:
        answer = json.loads(clear_code_markdown(raw_answer))
        if deep_dict_compare(answer, response_schema):
            answer2 = {'json': None}
        else:
            if isinstance(answer, dict) and ('array' == answer.get('type', '')) and isinstance(answer.get('items'), list):
                answer2 = {'json': answer['items']}
            elif answer.get('properties', False):
                answer2 = {'json': answer['properties']}
            else:
                answer2 = {'json': answer}
    except Exception:
        sys.stderr.write('cannot-evaluate => return as raw:>>>\n' + raw_answer + '<<<\n')
        sys.stderr.write(traceback.format_exc() + '\n')
        answer2 = {'raw': raw_answer}
    finally:
        answer2['model_base_url'] = OPENAI_BASE_URL
        answer2['model_name'] = model
        return answer2


def convert_mcp_to_openai_tool(mcp_tool: Any) -> Dict[str, Any]:
    """Maps an MCP tool object into an OpenAI-compatible function tool definition."""
    return {
        "type": "function",
        "function": {
            "name": mcp_tool.name,
            "description": mcp_tool.description or "Execute a web search or retrieval query.",
            "parameters": mcp_tool.inputSchema if hasattr(mcp_tool, "inputSchema") else mcp_tool.input_schema
        }
    }


async def with_mcp_chat_completion(instruction: str, response_schema: str, mcp_server_name: str, tools_model=OPENAI_TOOLS_MODEL, **chat_completions_args): ## TODO: final_model
    mcp_server_url = MCP_SERVERS[mcp_server_name]['mcp_server_url']
    mcp_headers = MCP_SERVERS[mcp_server_name].get('mcp_headers', {})
    openai_client = AsyncOpenAI()
    async with streamablehttp_client(url=mcp_server_url, headers=mcp_headers) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as mcp_session:
            # Initialize the session handshake
            await mcp_session.initialize()

            # 2. Fetch available web search tools from the remote server
            mcp_tools_response = await mcp_session.list_tools()
            available_mcp_tools = mcp_tools_response.tools
            allowed_tool_names = MCP_SERVERS[mcp_server_name].get('tool_names', [])
            forbidden_tool_names = MCP_SERVERS[mcp_server_name].get('forbidden_tool_names', [])
            filtered_mcp_tools = None
            prompt = calc_prompt(instruction, response_schema)
            prompt_hash = calc_md5(prompt)
            messages = [{"role": "user", "content": prompt}]
            is_final_llm_request = False
            is_messages_limit_reached = False
            final_response_content = None
            while True:
                try:
                    filtered_mcp_tools = available_mcp_tools
                    if allowed_tool_names:
                        filtered_mcp_tools = [t for t in filtered_mcp_tools if t.name in allowed_tool_names]
                    filtered_mcp_tools = [t for t in filtered_mcp_tools if not t.name in forbidden_tool_names]
                    openai_tools = [convert_mcp_to_openai_tool(t) for t in filtered_mcp_tools]
                    openai_tool_names = [t["function"]["name"] for t in openai_tools]
                    mcp_tool_map = {t.name: t for t in available_mcp_tools}
                    turn_idx = len(messages)
                    if len(messages) >= MESSAGES_LIMIT - 1:
                        is_messages_limit_reached = True
                        is_final_llm_request = True
                    if len(filtered_mcp_tools) == 0:
                        is_final_llm_request = True  ## TODO: use another multi-hops tool calls condition?
                    llm_response = None
                    if is_final_llm_request:
                        log_str(f"--- Sending final request to LLM: model={tools_model}, len(messages)={len(messages)}")
                        llm_response = await openai_client.chat.completions.create(
                            **chat_completions_args,
                            model=tools_model,
                            messages=messages,
                            response_format={"type": "json_object"}
                        )
                    else:
                        log_str(f"--- Sending request to LLM: model={tools_model}, tool_names={openai_tool_names}, len(messages)={len(messages)}")
                        llm_response = await openai_client.chat.completions.create(
                            **chat_completions_args,
                            model=tools_model,
                            messages=messages,
                            tools=openai_tools,
                            tool_choice="auto",
                            response_format={"type": "json_object"}
                        )
                    response_message = llm_response.choices[0].message
                    messages.append(response_message)
                    if is_final_llm_request:
                        final_response_content = response_message.content
                        if response_message.tool_calls:
                            log_str('warn: the final llm request return tool_calls instead of content')
                        break
                    else:
                        # Handle Tool Calls if the LLM decides to perform a web search
                        if response_message.tool_calls:
                            tools_added = 0
                            for tool_call_idx, tool_call in enumerate(response_message.tool_calls):
                                tool_name = tool_call.function.name
                                if tool_name not in openai_tool_names:
                                    log_str(f'error: invalid-tool, tool_name="{tool_name}", allowed_tool_names="{allowed_tool_names}"')
                                    raise RuntimeError('invalid-tool')
                                forbidden_tool_names.append(tool_name)
                                # Safely parse JSON arguments string into a dictionary
                                tool_args = json.loads(tool_call.function.arguments)

                                log_str(f"--- LLM requested tool execution: tool_name='{tool_name}' with arguments {tool_args}")

                                if tool_name in mcp_tool_map:
                                    ###
                                    # Call the tool remotely via the MCP session connection
                                    mcp_result = await mcp_session.call_tool(name=tool_name, arguments=tool_args)
                                    ###
                                    if mcp_result.isError:
                                        print(f"mcp-server-error: Tool returned an MCP error: {mcp_result.content}")
                                        raise RuntimeError('mcp-server-error')

                                    # Extract the string content from the MCP text response components
                                    content_text = "".join([
                                        content.text for content in mcp_result.content if hasattr(content, "text")
                                    ])

                                    # Use mcp_no_result_regex config to find no_result matchings in content_text
                                    for mcp_no_result_regex in MCP_SERVERS[mcp_server_name].get('no_results_regex', []):
                                        if mcp_no_result_regex and re.search(mcp_no_result_regex, content_text):
                                            log_str(f'mcp-no-result-error: mcp_no_result_regex="{mcp_no_result_regex}", content_text="' + content_text + '"\n---')
                                            raise RuntimeError('mcp-no-result-error')

                                    tool_result = {
                                        'tool_name': tool_name,
                                        'meta': {
                                            'initial_prompt_hash': prompt_hash,
                                            'request_hash': calc_json_hash(tool_args),
                                            'turn_idx': turn_idx,
                                            'tool_call_idx': tool_call_idx + 1,
                                            'tool_call_id': tool_call.id
                                        },
                                        'request':  tool_args,
                                        'response_text': content_text
                                    }
                                    log_str('Tool result:\n' + dump_json(create_trimmed_dict(tool_result, ['response_text'], '...'))) ## TODO: write to document storage cache

                                    # Feed the tool execution results back to the LLM context
                                    messages.append({
                                        "role": "tool",
                                        "tool_call_id": tool_call.id,
                                        "name": tool_name,
                                        "content": content_text
                                    })
                                    tools_added += 1
                                else:
                                    log_str(f"Error: Tool {tool_name} requested by LLM was not found on MCP server.")
                                    raise RuntimeError('not-found-tool')
                        else:
                            # Fallback if no web search was deemed necessary by the LLM
                            final_response_content = response_message.content
                            break
                        ##
                except openai.BadRequestError as e:
                    if e.code == "context_length_exceeded":
                        log_str(f"--- Context size limit hit: {e.message} -> try to drop last")
                        tools_added -= 1
                        messages.pop()
                        if tools_added < 0:
                            log_str(f"Error: context-length-exceeded, out of context: {e.message}")
                            raise RuntimeError('context-length-exceeded')
                        is_final_llm_request = True
                        continue
                    else:
                        log_str(f"Error: other Bad Request error: {e}")
                        raise e
                except openai.OpenAIError as e:
                    # Fallback catch for other OpenAI API anomalies (RateLimitError, AuthenticationError)
                    log_str(f"Error: OpenAI error occurred: {e}")
                    raise e
            log_str(f"--- LLM final response received")
            return final_response_content


def calc_module_name(func_name):
    return f'ai_function_templates/{func_name}'


def evaluate(func_name, input_data):
    meta = input_data.get('meta', {})
    template_string = read_string(f'{calc_module_name(func_name)}/prompt.md.j2')
    instruction = render_template(template_string, input_data)
    log_str(f'--- instruction meta: {json.dumps(meta)}\n')
    log_str(f'--- instruction:\n{instruction[0:MAX_LOGGING_LEN] + " ..."}\n')
    response_schema = read_yaml(f'{calc_module_name(func_name)}/output_schema.yaml')
    response = simple_chat_completion(instruction, response_schema, **meta)
    if response.get('json'):
        return response['json']
    else:
        log_str(f'--- invalid response:\n' + dump_json(response))
        raise RuntimeError('invalid-response')


async def async_evaluate2(func_name, input_data):
    meta = input_data.get('meta', {})
    model = meta.get('model', MODEL)
    tools_model = meta.get('tools_model', OPENAI_TOOLS_MODEL)
    temperature = meta.get('temperature', 0)
    template_string = read_string(f'{calc_module_name(func_name)}/prompt.md.j2')
    instruction = render_template(template_string, input_data)
    log_str(f'--- instruction meta: {json.dumps(meta)}\n')
    log_str(f'--- instruction:\n{instruction[0:MAX_LOGGING_LEN] + " ..."}\n')
    response_schema = read_yaml(f'{calc_module_name(func_name)}/output_schema.yaml')
    raw_answer = simple_chat_completion2(instruction, response_schema, model=model, temperature=temperature) if meta.get('mcp') is None else \
        await with_mcp_chat_completion(instruction,
                                       response_schema,
                                       meta['mcp'],
                                       tools_model=tools_model,
                                       temperature=temperature)
    answer2 = {}
    try:
        answer = json.loads(clear_code_markdown(raw_answer))
        if deep_dict_compare(answer, response_schema):
            answer2 = {'json': None}
        else:
            if isinstance(answer, dict) and ("array" == answer.get('type', '')) and isinstance(answer.get('items'), list):
                answer2 = {'json': answer['items']}
            elif answer.get('properties', False):
                answer2 = {'json': answer['properties']}
            else:
                answer2 = {'json': answer}
    except Exception:
        sys.stderr.write('cannot-evaluate => return as raw:>>>\n' + raw_answer + '<<<\n')
        sys.stderr.write(traceback.format_exc() + '\n')
        answer2 = {'raw': raw_answer}
    finally:
        answer2['model_base_url'] = OPENAI_BASE_URL
        answer2['model_name'] = model
        return answer2


async def async_evaluate(func_name, input_data):
    response = await async_evaluate2(func_name, input_data)
    if response.get('json'):
        return response['json']
    else:
        log_str(f'--- invalid response:\n' + dump_json(response))
        raise RuntimeError('invalid-response')
