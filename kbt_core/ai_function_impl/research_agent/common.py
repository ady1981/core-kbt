import httpx
import json
from markdownify import markdownify
from typing import Any


def jsonfy_agent_result(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple, set)):
        return [jsonfy_agent_result(child) for child in value]
    if isinstance(value, dict):
        return {str(key): jsonfy_agent_result(v) for key, v in value.items()}
    if hasattr(value, "model_dump_json"):
        try:
            dumped = value.model_dump_json(mode="json")
            return json.loads(dumped)
        except Exception:
            try:
                dumped = value.model_dump_json()
                return json.loads(dumped)
            except Exception:
                print(f'--- [warn]: cannot parse model_dump_json. Ignored. model_dump_json={value.model_dump_json()}')
                pass
    if hasattr(value, "dict"):
        try:
            return jsonfy_agent_result(value.dict())
        except Exception:
            print(f'--- [warn]: cannot parse dict. Ignored. dict={value.dict()}')
            pass
    if hasattr(value, "type"):
        payload: dict[str, Any] = {"type": value.type}
        for name in (
            "id",
            "name",
            "content",
            "content_blocks",
            "tool_calls",
            "invalid_tool_calls",
            "additional_kwargs",
            "response_metadata",
            "usage_metadata",
        ):
            if hasattr(value, name):
                payload[name] = jsonfy_agent_result(getattr(value, name))
        return payload
    if hasattr(value, "__dict__"):
        return {
            key: jsonfy_agent_result(child)
            for key, child in vars(value).items()
            if not key.startswith("_")
        }
    return str(value)


def create_rubric_result(
    agent_result: dict[str, Any],
    state: dict[str, Any],
) -> dict[str, Any]:
    evaluations = state.get("_rubric_evaluations", [])
    serialized_agent_result = jsonfy_agent_result(agent_result)
    last_message = serialized_agent_result.get('messages', [])[-1] if serialized_agent_result.get('messages', []) else None
    final_result = None
    if evaluations:
        last_evaluation = evaluations[-1]
        if last_evaluation['result'] == 'satisfied':
            final_result = {
                'status': 'ok',
                'details': {
                    'last_message': last_message
                }
            }
        else:
            final_result = {
                'status': 'error',
                'details': {
                    'last_evaluation_result': last_evaluation['result'],
                    'max_iterations': len(evaluations)
                }
            }
    return {
        'agent_result': serialized_agent_result,
        'evaluations': evaluations,
        'final_result': final_result,
    }


def fetch_webpage_content(url: str, timeout: float = 10.0) -> str:
    """Fetch and convert webpage content to markdown.

    Args:
        url: URL to fetch
        timeout: Request timeout in seconds

    Returns:
        Webpage content as markdown
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = httpx.get(url, headers=headers, timeout=timeout, follow_redirects=True)
        response.raise_for_status()
        return markdownify(response.text)
    except Exception as e:
        return f"Error fetching content from {url}: {str(e)}"

