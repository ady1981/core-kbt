from common import parse_yaml, dump_json
from ai_function import evaluate_function
from asyncio import run

FUN_NAME = 'merge_items_by_semantics'


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
    r = await evaluate_function(FUN_NAME, {'array_item_json_schema': array_item_json_schema, 'arrays': [left, right], 'merge_strategy': merge_strategy})
    print(dump_json(r))

run(main())