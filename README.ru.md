# Core-kbt

## Основная информация

Мини-фреймворк core-kbt (KBT = Knowledge Base Trajectory):
  - создан для упрощения разработки LLM-based приложений
  - предназначен для использования в качества компонента низшего уровня для приложений типа LLM Wiki.

Текущие фичи и подходы в core-kbt тезисно:

- архитектура ИИ-функций (AI-functions): возможность разработки интеллектуальных функций через написание теймплейтов для LLM-промпта и JSON Schema ответа, представленные как отдельные файлы
- генерация целевого MCP-сервера для AI-functions (TODO)
- архитектура для вычисления ИИ-функций через "процессы", которые упрощают кеширование и анализ ответов от LLM-провайдеров, и ускоряют цикл разработки, при возникновении ошибок
- интеграция с MCP-серверами инструментов (TODO)
- кеширование ответов от LLM tools для сохранения контекста, с возможностью перевычисления запроса другими моделями 
- универсальное представление LLM-промпта в структурированном виде
- онтология представление мета-знаний
- подход к LLM-промптингу на основе логических аспектов и спецификации схемы результата 
- реализация конкретных ИИ-функций: группа развития знаний
- реализация конкретных ИИ-функций: группа развития мета-знаний

Полезные примеры интеграции core-kbt:
- интеграция с Obsidian для развития знаний: https://github.com/ady1981/obsidian-templater-core-kbt
- пример решения универсальной задачи обоснованного выбора лучшего из двух вариантов: см. ИИ-функцию [concept_aspect_comparison](kbt_core%2Fai_function_impl%2Fconcept_aspect_comparison.py) и статьи [concept-comparison-n8n-example.ru.md](docs%2Fconcept-comparison-n8n-example.ru.md) и [concept-comparison-colab-example.ru.md](docs%2Fconcept-comparison-colab-example.ru.md)
- пример решения универсальной задачи удаления избыточных терминов из заданного списка без потери информации в рамках заданной перспективы: см. ИИ-функцию [concept_set_covering](kbt_core%2Fai_function_impl%2Fconcept_set_covering.py) и статью  [terms-reduction-colab-example.ru.md](docs%2Fterms-reduction-colab-example.ru.md)
- интеграция с MCP-серверами инструментов (TODO)

### Краткое введение

Сейчас понятно, что LLM способности являются революционными, но для раскрытия потенциала LLM способностей требуются специальные инструменты, при которых LLM способности используются по максимуму с оптимальными накладными расходами.   
Для того чтобы LLM способности использовать "правильно" **требуется** использовать особую архитектуру, в как можно более простом виде. **Архитектура такого типа не просматривается в существующих LLM фреймворках**. Поэтому, цель core-kbt - предоставить такой "правильный" инструмент (настраиваемый компонент), с "правильной" архитектурой.
Основные задачи:
* выявление требований для обще целевого программирования с точки зрения архитектуры и внедрение элементов этой архитектуры
* выявление способов и методов как повысить "эффективность" разработки LLM-based приложений и в области управления знаниями
* выявление мета-знаний, необходимых для развития и оптимизации знаний.

### Контекст и проблематика

Текущая проблематика; почему это важно; какие существуют ограничения:
- с LLM нужно взаимодействовать на естественном языке и нет эталона как нужно делать это правильно и эффективно
- для взаимодействия с LLM есть много ограничений, для которых нужны принципиальные решения
- для эффективного взаимодействия с LLM нужны представления доменных знаний, с правильной структурой
- возможности LLM дают работать со знаниями и нужно научится как это делать правильно
- есть ожидания, что конечную ценность будут иметь мета-знания, которые нужно выявлять.

### Методология

Текущие фичи и подходы в core-kbt:
- архитектура ИИ-функций (AI-functions): возможность разработки интеллектуальных функций через написание теймплейтов для LLM-промпта и JSON Schema ответа, представленные как отдельные файлы
- архитектура для вычисления ИИ-функций через "процессы", которые упрощают кеширование, трейсинг и анализ ответов от LLM-провайдеров,  ускоряют цикл разработки при возникновении ошибок
- универсальное представление LLM-промпта в структурированном виде
- онтология представление мета-знаний
- реализация конкретных ИИ-функций: группы развития знаний и мета-знаний
- подход к LLM-промптингу на основе логических аспектов и спецификации схемы результата.

### Результаты

Текущие результаты:
- архитектура ИИ-функций показывает свою эффективность за счет уникальной простоты
- архитектура вычисления ИИ-функций через "процессы" ускоряет цикл разработки
- универсальное представление LLM-промпта в структурированном виде показывает свою эффективность при итеративном улучшении качества ответов и ускорении скорости разработки новых эффективных промптов
- настроена эффективная интеграция с Obsidian и реализованы универсальные ИИ-функций для развития знаний
- сделан пример решения задачи обоснованного выбора лучшего из двух вариантов (см. ИИ-функцию concept_aspect_comparison)
- сделаны примеры интеграции с n8n ([1](docs%2Fconcept-comparison-n8n-example.ru.md)), Оbsidian ([1](https://github.com/ady1981/obsidian-templater-core-kbt)) и Colab ([1](docs%2Fconcept-comparison-colab-example.ru.md), [2](docs%2Fterms-reduction-colab-example.ru.md), [3](examples/colab/with-support-concept-aspect-comparison-demo3.ipynb))

### Планы на будущее

- больше примеров интеграции: вызов ИИ-функций из Jupyter-ноутбуков, интеграция с spreadsheets и умными-таблицами
- развитие мета-знаний и логико-аспектный подход к LLM-промпту
- разработка доменных знаний и мета-знаний для LLM-промпта
- разработка архитектуры агентов для развития и оптимизации знаний

## Начало работы

1. Клонируем репо:
```
git clone https://github.com/ady1981/core-kbt.git
cd core-kbt
```
2. Задаем значения переменных среды в `.env` файле, например для DeepSeek:
```shell
HOST=0.0.0.0
PORT=5001
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
OPENAI_API_KEY=<DEEPSEEK_API_TOKEN>
AI_FUNC_API_TOKEN=<A_SECRET>
```
2. Запускаем сервер AI-функций:
  * через docker:
```shell
./run-gh-docker-image.sh
```
   * через командную строку:
```shell
./runner.sh -s kbt-core/ai_function_server.py
```
3. Допустим мы хотим узнать столицу России. Будем использовать готовую AI-функцию `generate` с [промптом](ai_function_templates/generate/prompt.md.j2) и [JSON-схемой ответа](ai_function_templates/generate/output_schema.yaml).
Вызываем AI-функцию с соответствующими входными параметрами (`target_specification`):
```shell
source .env
curl -X PUT "http://127.0.0.1:5001/ai-func/generate" \
  -H "Api-Token: $AI_FUNC_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "{
  \"target_specification\": \"target_description: What is Capital of Russia?\"
}"
```
Ответ:
```
{
  "result": {
    "items": [
      {
        "item": "Moscow",
        "reasoning": "The target question asks for the capital of Russia. Based on general knowledge, the capital of Russia is Moscow."
      }
    ],
    "other_notes": "The information retrieval strategy specified no external context knowledge, relying solely on general knowledge to answer the factual question about the capital of Russia."
  }
}
```

## Развитие идеи

### Универсальный теймплейт для промпта

Понятно, что центральной темой для эффективного использования LLM является промпт-инжиниринг, т.е. подходы к построению эффективных запросов для получения нужных ответов.
Как известно, LLM всегда решает только одну задачу - generatively-continue-prompt. Можно записать общее представление с выделением различных частей для промпта так:
```yaml
LLM_prompt:  
  prompt_structure_and_notation_self_specification: []  
  target_specification:
  - task_specification  
  - task_description  
  - target_semantic_specification  
  - target_semantic_description    
  information_retrieval_strategy:  
  - context_knowledge_specification:  
    - context_knowledge_topic  
    - context_knowledge_source:  
        - properties  
        - content  
  - knowledge_sources_selection_strategy  
  - context_preparation_strategy  
  - contextual_alignment_strategy  
  - contextual_memory_strategy
  - ...  
  output_generation_strategy:  
  - execution_plan_specification  
  - task_decomposition_specification  
  - knowledge_consolidation_specification  
  - evaluation_metrics  
  - iteration_and_refinement_strategy  
  - examples  
  - safety_and_ethics_specification  
  - post_generation_verification_specification  
  - ...  
  output_specification:  
  - structure_and_formatting_specification  
  - output_constrains_specification  
  - output_content_strategy  
  - ...
  ```

Смысл этих частей промпта более-менее ясен из названия. Дополнительно отметим следующее:
* любая specification - задает спецификацию, т.е. однозначно понятные требования
* любая strategy - задает набор политик, как лучше достичь желаемого результата
* если task_specification задать сложно, то можно задать task_description. В дальнейшем результат генерации с таким промптом можно сравнить с результатов генерации для промпта с заданными соответствующим task_specification
* target_specification - задает спецификацию "смысла" запроса и результата
* information_retrieval_strategy - задает как найти информацию во внутренней базе, для решения запроса
* output_generation_strategy - задает стратегию, как генерировать ответ, чтобы прийти к нужному результату.

Приведем пример для промпта в этом представлении:
```yaml
LLM_prompt:
  target_specification:
  - task_specification: Abstractive summarize
  - target_semantic_specification: Concise  
  information_retrieval_strategy:
  - context_knowledge_specification:
    - context_knowledge_source: |
      {{TO_SUMMARIZE_TEXT}}
  - knowledge_sources_selection_strategy: Use only the provided input text.
  - contextual_alignment_strategy: Ensure summary reflects the core meaning of the input.
  output_generation_strategy:
  - focus_on: the central theme
  - execution_plan_specification: Read input, identify key sentences/concepts, synthesize into a short paragraph.
  - task_decomposition_specification: Single step.
  - knowledge_consolidation_specification: Extract and combine main ideas.
  - evaluation_metrics: Conciseness, Fidelity to source.
  - safety_and_ethics_specification: Maintain factual accuracy.
  - post_generation_verification_specification: Check if summary is significantly shorter than the original.
  output_specification:
  - structure_and_formatting_specification: Plain text paragraph.
  - output_constrains_specification: Maximum 3 sentences.

```
Отметим, что существование эффективного универсального теймплейта для LLM промпта означает, что можно сделать одну условно универсальную AI-функцию, через которую можно задать для LLM любую задачу. Причем настраивать такой LLM промпт можно по некоторой универсальной системе аспектов. Однако, для большего удобства и повышения эффективности LLM промптов для выделенных задач имеет смысл создавать отдельные AI-функции, в которых можно более конкретно определять входные поля и, что еще более важно, в выходной JSON-Schema определять более конкретные выходные поля (в том числе для того, чтобы "заставить" модель "подумать" над генерируемыми значениями).
