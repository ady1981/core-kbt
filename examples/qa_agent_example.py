"""
Example usage of calc_answer from qa_agent
"""
import json
import os

from kbt_core.ai_function_impl.research_agent.agent.qa_agent import calc_answer

OPENAI_MODEL = os.environ["OPENAI_MODEL"]


def main():
    source_content = """
    The QuickPay payment processing system supports credit cards, debit cards, 
    and bank transfers. All transactions are encrypted using TLS 1.3. 
    The average processing time for credit card transactions is 2.3 seconds.
    """
    
    qa_query = "What payment methods does QuickPay support?"
    
    model = OPENAI_MODEL
    max_iterations = 2
    
    result = calc_answer(
        source_content=source_content,
        qa_query=qa_query,
        model=model,
        max_iterations=max_iterations
    )
    
    print("=== QA Agent Example ===\n")
    print(f"Question: {qa_query}\n")
    
    if result.get("final_result", {}).get("status") == "ok":
        response_content = result.get("final_result", {}).get("details", {}).get("last_message", {}).get("content", "{}")
        try:
            parsed_response = json.loads(response_content)
            print(f"Answer: {parsed_response.get('answer', 'N/A')}")
            print(f"\nAnswer Support:")
            for quote in parsed_response.get('answer_support', []):
                print(f"  - {quote}")
        except json.JSONDecodeError:
            print(f"Raw response: {response_content}")
    else:
        print(f"Status: {result.get('final_result', {}).get('status')}")
        print(f"Details: {result.get('final_result', {}).get('details')}")
    
    print(f"\nFull result: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    main()