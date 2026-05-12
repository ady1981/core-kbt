Как известно, LLM - это машина, которая "видела" "весь Интернет" и много чего запомнила. Задавая ей правильные вопросы можно получать "правильные" ответы (где "правильные" стоит понимать в статистическом смысле). Широта и универсальность таких способностей дает возможность ставить новые универсальные задачи и получать общее решение таких задач.

Например, рассмотрим универсальную задачу "обоснованного выбора лучшего решения из двух вариантов". В этой задаче требуется описать контекст, в котором требуется сделать выбор (`observer_context_description`) и два понятия (`a_concept` и `b_concept`), каждое из которых описывает альтернативное решение. Для этой задачи в фреймворке core-kbt есть решение: ИИ-функция [concept_aspect_comparison](https://github.com/ady1981/core-kbt/blob/master/kbt_core/ai_function_impl/concept_aspect_comparison.py)

Реализация ИИ-функции `concept_aspect_comparison` работает примерно так:
- определяется "общее вышестоящее понятие" для понятий `a_concept` и `b_concept`: по этому [промпту](https://github.com/ady1981/core-kbt/blob/master/ai_function_templates/superordinate_concept_identification/prompt.md.j2) и этой [JSON Schema результата](https://github.com/ady1981/core-kbt/blob/master/ai_function_templates/superordinate_concept_identification/output_schema.yaml)
- для общего вышестоящего понятия запрашиваются аспектные признаки и все остальные существенные признаки для этой задачи: [промпт](https://github.com/ady1981/core-kbt/blob/master/ai_function_templates/perspective_features/prompt.md.j2), [JSON Schema результата](https://github.com/ady1981/core-kbt/blob/master/ai_function_templates/perspective_features/output_schema.yaml)
- запрашивается сравнение для понятий `a_concept` и `b_concept`, для каждого аспекта: [промпт](https://github.com/ady1981/core-kbt/blob/master/ai_function_templates/perspective_feature_comparison/prompt.md.j2), [JSON Schema результата](https://github.com/ady1981/core-kbt/blob/master/ai_function_templates/perspective_feature_comparison/output_schema.yaml)
- т.е. LLM модель определяет общее вышестоящее понятие (и все остальные существенные признаки для этой задачи), аспектные признаки, значения весов для аспектов и признаков, и отдельно определяет "победителя" по каждому аспектному признаку
- готово: итоговый результат cравнения точно вычисляется (в том числе результат сравнения нормируется, чтобы получить значения в процентах).

ИИ-функцию `concept_aspect_comparison` функцию можно также вызывать из Google Colab ноутбука и мы можем продемонстрировать [пример ноутбука](https://github.com/ady1981/core-kbt/blob/master/examples/colab/concept-aspect-comparison-demo1.ipynb) с решением этой задачи для 5 примеров **в совершенно разных областях**:
- **1. Выбор оптимального фреймворка для разработки нового микросервиса:** ![](https://habrastorage.org/webt/13/d5/f6/13d5f60a79b8db3a30a6a214be350c29.png)
- **2. Выбор лучшего метода хранения данных для долгосрочного архива:** ![](https://habrastorage.org/webt/d3/e3/a2/d3e3a2c0c952ab2897e1a2e809d0e6db.png)
- **3. Выбор лучшей стратегии для снижения углеродных выбросов в крупном городе:** ![](https://habrastorage.org/webt/04/68/db/0468dbc1008916caf73b74bd2ebacdc1.png)
- **4. Выбор антисептика для бытовой обработки небольшой раны у ребёнка:** ![](https://habrastorage.org/webt/60/04/b0/6004b0ac93814318c2015420a66f77ff.png)
- **5. Выбор смартфона для фрилансера-дизайнера:** ![](https://habrastorage.org/webt/1f/c8/e9/1fc8e9d0bcfeb290ec5b7bbdfea4e5e7.png)

С другими деталями о core-kbt мини-фреймворке можно ознакомиться в этой [статье](https://habr.com/ru/articles/1030630/).

Итого, что можно было узнать в этой статье:
- описание логики ИИ-функции [concept_aspect_comparison](https://github.com/ady1981/core-kbt/blob/master/kbt_core/ai_function_impl/concept_aspect_comparison.py)
- [пример](https://github.com/ady1981/core-kbt/blob/master/examples/colab/concept-aspect-comparison-demo1.ipynb) как ИИ-функцию `concept_aspect_comparison` можно вызывать из среды Google Colab
- 5 примеров решения задачи "обоснованного выбора лучшего решения из двух вариантов" в совершенно разных областях, от проблемы выбора антисептика для бытовой обработки небольшой раны у ребёнка до выбора лучшей стратегии для снижения углеродных выбросов в крупном городе

---

Отзывы, предложения и любая обратная связь приветствуется.
