import hashlib
import json
import os
import re
import sys
from urllib.parse import urlparse

import yaml
from langchain_openai import ChatOpenAI

from kbt_core.ai_function_impl.research_agent.agent.qa_agent import calc_answer
from kbt_core.ai_function_impl.research_agent.raw_storage import write_document
from kbt_core.ai_function_impl.research_agent.tavily_helper import web_search

QA_OPENAI_MODEL = os.environ.get('QA_OPENAI_MODEL', os.environ['OPENAI_MODEL'])
MAX_ITERATIONS = int(os.environ.get('QA_MAX_ITERATIONS', '2'))

def with_frontmatter(md_document: str, frontmatter_props: dict) -> str:
    frontmatter_yaml = yaml.dump(frontmatter_props, default_flow_style=False)
    return f"---\n{frontmatter_yaml}---\n{md_document}"


def clear_prefix(s):
    return re.sub(r'```(.*)\n', '', s)

def clear_suffix(s):
    return s.removesuffix('```')


def calc_result(qa_model, web_search_limit_n, topic_keyword, qa_query):
    limit_n = int(os.environ.get('TAVILY_LIMIT_N', '1'))
    results = web_search(qa_query, web_search_limit_n)
    qa_model = ChatOpenAI(
        model=qa_model,
        base_url=os.environ.get("OPENAI_BASE_URL"),
        api_key=os.environ.get("OPENAI_API_KEY"),
        temperature=0.0,
    )

    for result in results:
        url = result['url']
        content = result['content']
        version = 'ordinal.1'
        parsed_url = urlparse(url)
        site_context_url = parsed_url.netloc
        site_context_path = parsed_url.path
        content_sha256hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        content2 = with_frontmatter(content, {
            'original_query': qa_query,
            'url': url,
            'site_context_url': site_context_url,
            'site_context_path': site_context_path,
            'content_sha256hash': content_sha256hash
        })
        content_filepath = write_document(topic_keyword, site_context_url, version, content_sha256hash, content2)
        print(f"Found content saved: {content_filepath}", file=sys.stderr)

        total_result = calc_answer(content, qa_query, qa_model, MAX_ITERATIONS)
        final_result = total_result['final_result']
        if final_result['status'] == 'error':
            continue
        result_content = final_result['details'].get('last_message', {}).get('content')
        result_content = clear_prefix(result_content)
        result_content = clear_suffix(result_content)
        result_content2 = json.loads(result_content)
        if result_content2.get('answer') == 'No_answer_found':
            continue
        result_content2['answer_source'] = content_filepath
        answer = result_content2
        print(json.dumps(answer, indent=2))
        return answer

    answer = {
        'status': 'error',
        'details': {
            'error_code': 'cannot-find-answer',
            'web_search_limit_n': limit_n,
            'rubric_max_iterations': MAX_ITERATIONS
        }
    }
    print(json.dumps(answer, indent=2))
    return answer


async def evaluate(input_data):
    meta = input_data.get('meta', {})
    qa_model = meta.get('qa_model', meta.get('model', None))
    (topic_keyword, qa_query, web_search_limit_n) = (input_data['topic_keyword'], input_data['qa_query'], input_data['web_search_limit_n'])
    return calc_result(qa_model, web_search_limit_n, topic_keyword, qa_query)
