import asyncio
import os

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, stdio_client
from mcp.client.sse import sse_client
from openai import OpenAI

from common import dump_json

load_dotenv()

OPENAI_MODEL = os.environ['OPENAI_MODEL']
YANDEX_SEARCH_API_KEY = os.environ['YANDEX_SEARCH_API_KEY']
YANDEX_SEARCH_FOLDER_ID = os.environ['YANDEX_SEARCH_FOLDER_ID']

# 1. Initialize your LLM Client
openai_client = OpenAI()

# Remote MCP server URL (update with your actual server URL)
MCP_SERVER_URL = os.environ.get('MCP_SERVER_URL', 'https://d5de9siimt9bkld7viic.emzafcgx.apigw.yandexcloud.net:3000/sse')

async def run_mcp_client():
    # 3. Establish communication with the MCP server
    async with sse_client(url=MCP_SERVER_URL, headers={'ApiKey': YANDEX_SEARCH_API_KEY, 'FolderId': YANDEX_SEARCH_FOLDER_ID, 'Content-Type': 'application/json', 'Accept': 'text/event-stream'}) as (read_stream, write_stream):
    # async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the session handshake
            await session.initialize()

            # 4. Fetch the available tools exposed by the server
            mcp_tools = await session.list_tools()

            # 5. Map MCP tools to OpenAI's function-calling JSON format
            openai_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                }
                for tool in mcp_tools.tools
            ]

            # 6. Ask the LLM a question, passing the translated tools
            messages = [{"role": "user", "content": "Какая погода сейчас в Москве?"}]

            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                tools=openai_tools if openai_tools else None
            )

            tool_calls = response.choices[0].message.tool_calls

            # 7. If the LLM decides to call an MCP tool, execute it through the server
            if tool_calls:
                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = eval(tool_call.function.arguments)  # Safe parsing suggested for json

                    print(f"🤖 LLM requested tool: {tool_name} with args {tool_args}")

                    # Call the actual tool via the MCP server session
                    result = await session.call_tool(tool_name, arguments=tool_args)
                    print(f"🛠️ MCP Server Result:" + dump_json(result.content))


# Execute the async client
asyncio.run(run_mcp_client())
