import json
import os
from asyncio import run

from dotenv import load_dotenv

from ai_function import evaluate_function
from ai_function_impl.concept_set_covering import calc_concept_set_covering
from kbt_core.ai_function_impl import concept_set_covering
from common import dump_json, with_model_input_data, write_json

load_dotenv()

AI_FUN_NAME = 'concept_set_covering'
OPENAI_MODEL = os.environ["OPENAI_MODEL"]


async def calc_method1():
    observer_context_description = 'Рассматриваются живые организмы в биологической систематике.'
    frame_of_reference = 'Unbiased framework' ## 'Common sense'
    print(dump_json(await concept_set_covering.calc_perspective(observer_context_description, frame_of_reference)))


async def calc_method2():
    member_of = {
        'Пользовательский интерфейс': ['Пользовательский интерфейс', 'Интерфейс пользователя', 'Фронтенд'],
        'Интерфейс пользователя': ['Интерфейс пользователя', 'Пользовательский интерфейс', 'Фронтенд'],
        'Фронтенд': ['Фронтенд', 'Пользовательский интерфейс', 'Интерфейс пользователя'],
        'Серверная часть': ['Серверная часть', 'Бэкенд'],
        'Бэкенд': ['Бэкенд', 'Серверная часть'],
        'База данных': ['База данных', 'Хранилище данных'],
        'Хранилище данных': ['Хранилище данных', 'База данных']
    }
    concepts = ['Пользовательский интерфейс', 'Интерфейс пользователя', 'Фронтенд', 'Серверная часть', 'Бэкенд', 'База данных', 'Хранилище данных']
    perspective = {
        "basis_of_consideration": "Creating a glossary for an internal software development guide from a developer's perspective, focusing on subtype membership and ignoring functional relationships.",
        "perspective_observer_strategy": "Identify full perspective representation by classifying terms based on their subtype hierarchies, excluding any functional or behavioral aspects.",
        "point_of_view": "Developer-centric, emphasizing structural taxonomy over functional interactions."
    }
    perspective_concept_relations = await concept_set_covering.calc_perspective_concept_relations(None, concepts, perspective)
    concept_relations_map = concept_set_covering.calc_concept_relations_map(concepts, perspective_concept_relations)
    print('concept_relations_map:\n' + dump_json(concept_relations_map))
    (set_covering_ids, eliminated_ids) = calc_concept_set_covering(concepts, concept_relations_map)
    print('set_covering_ids:', set_covering_ids)
    print('eliminated_ids:', eliminated_ids)


async def main():
    # observer_context_description = 'Рассматриваются живые организмы в биологической систематике'
    # concepts = ['Растения', 'Животные', 'Человек', 'Люди']
    # concepts = ['Киты', 'Дельфины', 'Китообразные', 'Рыбы', 'Приматы', 'Человек'] ## 'Млекопитающие'

    # observer_context_description = 'Каталог компьютерных комплектующих. Учитывать, что все компоненты поставляются в несобранном виде. Существенные признаки: принадлежность к подтипу, игнорировать функциональные отношения'
    # # concepts = 'CPU, motherboard'.split(', ')
    # concepts = 'CPU, RAM, hard drive, motherboard, video card, SSD, NVMe, Nvidia GeForce RTX 50'.split(', ')

    # observer_context_description = 'Описание этапов разработки программного обеспечения для заказчика. Гранулярность рассмотрения - низкая'
    # concepts = 'Планирование, Анализ требований, Кодирование, Тестирование, Развертывание, Фаза инициации, Фаза исполнения, Фаза завершения, Приемочное тестирование'\
    #             .split(', ')

    # observer_context_description = 'Архитектура микросервисной системы, где свойства определяются уровнем абстракции и функциональной областью.'
    # concepts = 'Сервис аутентификации, База данных пользователей, API Gateway, Управление доступом, Внешний интерфейс'\
    #             .split(', ') ## Безопасность

    # observer_context_description = 'Административно-территориальное деление России. Существенные признаки - вхождение в более крупные единицы'
    # concepts = 'Москва, Центральный федеральный округ, Московская область, Город федерального значения, Санкт-Петербург, Ленинградская область, Северо-Западный федеральный округ'.split(', ')

#     observer_context_description = 'Создание глоссария для внутреннего руководства по разработке программного обеспечения.'
#     concepts = '''Пользовательский интерфейс
# Интерфейс пользователя
# Клиентская часть приложения
# Фронтенд
# Серверная часть
# Бэкенд
# База данных
# Хранилище данных'''.split('\n')

    observer_context_description = 'Мы готовим обзорную статью по теме "Использование машинного обучения для улучшения пользовательского опыта в электронной коммерции". Нам необходимо составить максимально лаконичный набор ключевых тем/идей для этой статьи.'
    concepts = '''Машинное обучение
Персонализация
Электронная коммерция
Рекомендательные системы
Алгоритмы ранжирования товаров
Искусственный интеллект
Поведенческий анализ пользователей
Увеличение конверсии
Динамическое ценообразование на основе ML
Прогнозирование оттока клиентов
Индивидуальные предложения
Оптимизация пользовательского пути
Глубокое обучение
Сегментация клиентов'''.split('\n')

    frame_of_reference = 'Unbiased logical framework' ## 'Common sense'
    input_data = {
        'observer_context_description': observer_context_description,
        'concepts': concepts,
        'frame_of_reference': frame_of_reference,
    }
    r = await evaluate_function(AI_FUN_NAME, with_model_input_data(input_data, OPENAI_MODEL))
    print('=== Response:\n' + dump_json(r))
    formatted_model_name = OPENAI_MODEL.strip().replace('/', '-').replace('.', '-')
    # write_yaml(json_response, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.yaml')
    write_json(r, f'temp/{AI_FUN_NAME}.{formatted_model_name}.response.json')


run(calc_method2())
# run(main())