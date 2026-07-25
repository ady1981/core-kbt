import json
from pathlib import Path

import yaml
from deepagents import RubricMiddleware, create_deep_agent
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from ..common import create_rubric_result


def invoke_qa_agent(source_content, qa_query, response_json_schema, model, max_iterations, checkpointer):
    system_prompt = (
        "<INSTRUCTIONS>\n"
        "You are a precise and accurate QA assistant. Your task is to answer questions based solely on "
        "the provided source document.\n"
        "INSTRUCTIONS:\n"        
        "1. Read the source document carefully\n"
        "2. Answer the question using ONLY information found in the document\n"
        "3. Be concise and direct in your answers\n"
        "4. If the answer is in the document, quote the relevant portion\n"        
        "5. Do not make assumptions or use other sources\n"
        "6. If the question cannot be answered based on the document, respond with an answer value: No_answer_found\n"
        "7. Respond strictly with a response matching the provided RESPONSE_JSON_SCHEMA\n"
        "</INSTRUCTIONS>\n"
        f"<SOURCE_DOCUMENT>\n{source_content}\n</SOURCE_DOCUMENT>\n"
        f"<QUESTION>{qa_query}</QUESTION>\n"
        f"<RESPONSE_JSON_SCHEMA>{json.dumps(response_json_schema)}</RESPONSE_JSON_SCHEMA>"
    )

    agent = create_deep_agent(
        model=model,
        middleware=[
            RubricMiddleware(
                model=model,
                max_iterations=max_iterations
            ),
        ],
        checkpointer=checkpointer,
    )

    config = {
        "configurable": {
            "thread_id": "rubric-thread"
        }
    }
    
    agent_result = agent.invoke(
        {
            "messages": [HumanMessage(system_prompt)],
            "rubric": (
                f"The \"answer\" directly answer the initial question ('{qa_query}') and the \"answer_support\" contains source exact quotes for the \"answer\" OR the \"answer\" is \"No_answer_found\"\n"
            ),
        },
        config=config,
    )

    state = agent.get_state(config).values

    return (agent_result, state)


def calc_answer(source_content, qa_query, model, max_iterations):
    schema_path = Path(__file__).parent.parent.parent / 'json_schema' / 'qa_result_response_schema.yaml'
    response_json_schema = yaml.safe_load(schema_path.read_text())
    checkpointer = InMemorySaver()
    agent_result, state = invoke_qa_agent(source_content, qa_query, response_json_schema, model, max_iterations, checkpointer)
    total_result = create_rubric_result(agent_result, state)
    return total_result
