import os

from dotenv import load_dotenv

from common import parse_yaml, dump_json, with_model_input_data
from ai_function import evaluate_function
from asyncio import run

load_dotenv()

AI_FUN_NAME = 'merge_items_by_semantics'
OPENAI_MODEL = os.environ["OPENAI_MODEL"]


async def main():
    left = ["codeGeneration","conversationalAgent","informationExtraction","textSummarization","languageTranslation","questionAnswering","textGeneration","textClassification"]
    right = ["TextRewritingTask","LanguageTranslationTask","InformationExtractionTask","TextClassificationTask","TextGenerationTask","SummarizationTask"]
    array_item_json_schema = parse_yaml('''
type: array
items:
  - type: string
    description: a task type for LLM
''')
    merge_strategy = {'not_comparable': 'merge', 'comparable_not_equal': 'merge'}
    # merge_strategy = {}
    r = await evaluate_function(AI_FUN_NAME, with_model_input_data({
        'array_item_json_schema': array_item_json_schema,
        'arrays': [left, right],
        'merge_strategy': merge_strategy
    }, OPENAI_MODEL))
    print(dump_json(r))

run(main())