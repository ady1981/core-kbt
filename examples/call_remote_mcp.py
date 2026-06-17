import os
import asyncio
from typing import Any, Dict, List
from openai import AsyncOpenAI

from mcp import ClientSession
from mcp.client.sse import sse_client
from dotenv import load_dotenv
import json

load_dotenv()

# OPENAI_BASE_URL = "http://localhost:1234/v1"
# OPENAI_API_KEY = "not-needed-for-local"
OPENAI_MODEL = os.environ['OPENAI_MODEL']

## Example (local MCP server):
## uvx duckduckgo-mcp-server --transport sse

# Remote MCP Server endpoint details
MCP_SERVER_SSE_URL = "http://127.0.0.1:8000/sse"
# Set token if your remote server requires Authorization, otherwise leave as None
MCP_AUTH_TOKEN = ""

# Initialize the OpenAI-compatible client
openai_client = AsyncOpenAI() ##base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY

def get_mcp_headers() -> Dict[str, str]:
    """Generates request headers, adding optional authorization if available."""
    headers = {"Content-Type": "application/json"}
    if MCP_AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {MCP_AUTH_TOKEN}"
    return headers


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


async def workflow(user_prompt: str):
    # 1. Establish connection with the remote SSE MCP server
    headers = get_mcp_headers()

    print(f"Connecting to remote MCP server at {MCP_SERVER_SSE_URL}...")
    async with sse_client(url=MCP_SERVER_SSE_URL, headers=headers) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as mcp_session:
            # Initialize the session handshake
            await mcp_session.initialize()

            # 2. Fetch available web search tools from the remote server
            mcp_tools_response = await mcp_session.list_tools()
            available_mcp_tools = mcp_tools_response.tools

            # Map tools to OpenAI schema definitions
            openai_tools = [convert_mcp_to_openai_tool(t) for t in available_mcp_tools]
            tool_names = [t["function"]["name"] for t in openai_tools]
            mcp_tool_map = {t.name: t for t in available_mcp_tools}

            messages = [{"role": "user", "content": user_prompt}]

            is_final_llm_request = False
            final_response_content = None
            while True:
                try:
                    print(f"Sending request to LLM: {OPENAI_MODEL}, tool_names={tool_names}, len(messages)={len(messages)}")
                    llm_response = await openai_client.chat.completions.create(
                        model=OPENAI_MODEL,
                        messages=messages,
                        tools=openai_tools,
                        tool_choice="auto"
                    )
                    response_message = llm_response.choices[0].message
                    messages.append(response_message)
                    if is_final_llm_request:
                        final_response_content = response_message.content
                        break
                    else:
                        # Handle Tool Calls if the LLM decides to perform a web search
                        if response_message.tool_calls:
                            tools_added = 0
                            for tool_call in response_message.tool_calls:
                                tool_name = tool_call.function.name
                                # Safely parse JSON arguments string into a dictionary
                                tool_args = json.loads(tool_call.function.arguments)

                                print(f"LLM requested tool execution: tool_name='{tool_name}' with arguments {tool_args}")

                                if tool_name in mcp_tool_map:
                                    # Call the tool remotely via the MCP session connection
                                    mcp_result = await mcp_session.call_tool(name=tool_name, arguments=tool_args)

                                    # Extract the string content from the MCP text response components
                                    content_str = "".join([
                                        content.text for content in mcp_result.content if hasattr(content, "text")
                                    ])

                                    # Feed the tool execution results back to the LLM context
                                    messages.append({
                                        "role": "tool",
                                        "tool_call_id": tool_call.id,
                                        "name": tool_name,
                                        "content": content_str
                                    })
                                    tools_added += 1
                                else:
                                    print(f"Error: Tool {tool_name} requested by LLM was not found on MCP server.")
                                    raise RuntimeError('not-found-tool')
                        else:
                            # Fallback if no web search was deemed necessary by the LLM
                            final_response_content = response_message.content
                            break
                        ##
                except openai.BadRequestError as e:
                    if e.code == "context_length_exceeded":
                        print(f"Context size limit hit: {e.message} -> try ")
                        tools_added -= 1
                        messages.pop()
                        if tools_added < 0:
                            print(f"Out of context: {e.message}")
                            raise RuntimeError('out-of-context')
                        is_final_llm_request = True
                        continue
                    else:
                        print(f"Other Bad Request error: {e}")
                        raise e
                except openai.OpenAIError as e:
                    # Fallback catch for other OpenAI API anomalies (RateLimitError, AuthenticationError)
                    print(f"OpenAI error occurred: {e}")
                    raise e
            print(f"LLM final response:\n" + final_response_content)


if __name__ == "__main__":
    # Test query requiring recent or specific web information
    # query = sys.argv[1]
    # query = 'What is best agentic web search in 2026?'
    # query = 'In a context of Kubernetes. How to collect kubernetes events via vector utility?'
#     query = '''Aspect: Долгосрочная поддерживаемость и стабильность
# Feature: Стабильность API фреймворка
# Superordinate_concept:	Web Application Frameworks
# Point_of_view: Decision-maker selecting a framework for a medium-sized microservice under a 60-day launch constraint
# Task: верно ли, что "FastAPI (Python)" лучше чем "Gin (Go)" по значению этого аспектного свойства?
# Possible answers: 1, 0, undefined
# Answer only highly likelihood final answer and nothing else. Search on the Internet before final answer if you are unsure.
# '''
    asyncio.run(workflow(query))
