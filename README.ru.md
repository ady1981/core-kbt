## Концепция проекта

Проект core-kbt (kbt - это аббревиатура от Knowledge Base Trajectory) - это мини-фреймворк для разработки LLM-based приложений и доменных баз знаний, с примерами доменных знаний из областей представления знаний, LLM и средств разработки.

Идею проекта можно представить с разных сторон:
* сделать удобные средства разработки для LLM-based приложений
* разработать и использовать подход, при котором оптимизировать промпты для задачи нужно через оптимизацию контекста, который вычисляется из базы знаний задачи (доменной базы знаний)
* проект является вариантом развития идеи prompting-as-code.

### Со стороны удобства разработки

Для практической разработки приложения, использующего LLM:
* необходимо иметь четкую модель данных того, что нужно подавать LLM на вход и получать на выходе
* удобные возможности создавать новые AI-функции с предсказуемыми свойствами
* работать с schema-less данными, но с фиксацией как JSON-схемы, так и семантической-схемы (онтологии), когда это необходимо
* удобно просматривать и модифицировать данные, которые являются контекстом для LLM-промптов
* кешировать ответы от LLM
* распараллеливать запросы к провайдерам LLM с контролируемым значением requests-per-second.

### Со стороны представления знаний

Новые возможности, которые дают технологии GenAI, требуют новых подходов к представлению знаний и методов программирования.
LLM модели пропустили через универсальные алгоритмы большие объемы текстовой информации и следует ожидать, что внутреннее представление LLM модели о мире будет соответствовать тому как люди представляют знания. Самым близким к человеческому способом представления знаний является онтологическое представление. Поэтому следует ожидать, что именно онтологическое представление будет мостом между "миром представлений LLM" и человеческим представлением знаний, которое необходимо для эффективного решения практических задач.

Предлагается использовать следующий верхне-уровневый более-менее универсальный подход к решению задачи с помощью LLM: 
  * разработать верхне-уровневую онтологию, которая должна удобна и понятна LLM и человеку: [ontology-kb-classes/_all.yaml](elementary%2Fontology-kb-classes%2F_all.yaml)
  * разработать типичные доменные онтологии, которые можно использовать для конкретных задач (пример: [comparison-kb-classes/_all.yaml](elementary%2Fcomparison-kb-classes%2F_all.yaml))
  * решать задачу в следующей постановке:
    разделить информацию по задаче на следующие блоки (`<я, как исследователь проблемы с помощью LLM, описываю ...>`): 
    * `<что я знаю>`: в виде базы знаний на основе онтологии
    * `<что я хочу узнать>`: в виде задачи в сущностях базы знаний
    * `<что я хочу сгенерировать>`: в виде задачи в сущностях базы знаний.

Постепенно формулируя задачи в сущностях базы знаний и решая эти задачи мы будем постепенно пополнять базу знаний. До тех пор, пока в базе знаний не появятся сущности, в которых содержатся ответы, для которых эта задача и была создана.

## Для чего полезен фреймворк

* AI-функции для быстрого создания и использования функций для обработки информации через LLM, со структурированным ответом
* база данных для YAML/JSON-сущностей в файловом представлении: быстрый и удобный ввод данных для обработки через AI, удобное редактирование сущностей до и после AI обработки
* если JSON-схемы для YAML/JSON-сущностей недостаточно, для углубления знания для решения задачи нужна последовательная разработка доменной онтологии для этой задачи: можно использовать готовую верхне-уровневую онтологию как базу для создания доменной онтологии: см. [ontology-kb-classes/_all.yaml](elementary%2Fontology-kb-classes%2F_all.yaml)
* разработка траекторий доменных баз знаний: YAML/JSON-сущности и состояние базы знаний хранится как файлы в git, что делает удобным мутации значений сущностей базы знаний через git-бранчевание для дальнейшей оптимизации и поиска лучшего состояния базы знаний
* можно настроить CI pipeline для git-репозитория с запуском сервера AI-функций: в результате получится удобный цикл разработки AI-функций и поддержки доменной базы знаний
* персистентные процессы для удобной реализации логики обработки, планирования обработки, кеширования ответов от внешних сервисов и отладки.

## Фичи фреймворка

* AI-функция со структурированным ответом (см. [ai_functions](ai_functions)):
  * каждой AI-функции соответствует папка c теймплейтом промпта и JSON-схема для ответа:  
    * j2 теймплей для промпта (например: [prompt.md.j2](ai_functions/list_best_tasks_for_llm_effectivess/prompt.md.j2))
    * требуемая JSON схема для ответа (например: [output_schema.yaml](ai_functions/list_best_tasks_for_llm_effectivess/output_schema.yaml))
  * есть `evaluate` метод для вызова AI-функции: [ai_function.py](kbt-core/ai_function.py)
  * есть серверное приложение для динамического web API для вызова любой AI-функции:
    * сервер: [ai_function_server.py](kbt-core%2Fai_function_server.py)
    * сервер авторизует все запросы по API-токену (секрету)
    * пример клиента: [ai_function_client.py](examples%2Fai_function_client.py)
* структурированное представление YAML/JSON-сущностей (см. [elementary](elementary)):
  * каждой сущности соответствует папка с элементами сущностей, представленными как файлы
  * для удобства редактирования, значение для поля сущности может подгружаться из файла
  * есть API для работы с сущностями: см. [items_db.py](kbt-core/items_db.py)
* готовый вариант верхне-уровневой базовой онтологии небольшого размера, которая понятна LLM и человеку: [ontology-kb-classes/_all.yaml](elementary%2Fontology-kb-classes%2F_all.yaml)
* персистентные процессы для удобной реализации логики обработки, планирования обработки, кеширования ответов от внешних сервисов и отладки (см. [processes](processes)):
  * персистентный процесс имеет input (входные данные для процесса), state (текущее состояние процесса) и `status`: `initial` -> `running` -> (`terminated` | `error`) 
  * процессы могут запускаться асинхронно в заданное количество потоков
  * для каждого процесса создается input файл в JSON с входными данными для этого процесса (в папке [processes/input](processes/input)) и state файл процесса в JSON (в папках [processes/by_status](processes/by_status)), в который процесс может записать своё персистентное состояние, и в который записывается результат процесса, когда процесс переходит в `status=terminated` (папка [processes/by_status/terminated](processes/by_status/terminated))
  * логика процесса описывается в файле модуля процесса в папке: [processes/implementation](processes/implementation)
  * процесс определяет как вычисляется его ID в методе `calc_input_id` 
  * создание процесса описывается в соответствующих модулях или скриптах.

## Направления дальнейшего развития проекта

* интеграция с Langfuse для traceability и оценки качества промптов
* интеграция с Wikidata (поиск и загрузка Wikidata items как сущности в elementary)
* вычисление AI-функцией через пользовательский python метод `evaluate` и использование других AI-функций при вычислении значения AI-функций   
* примеры оптимизации промптов через траекторию доменных баз знаний
* разработка инструментов для проведения исследования в выбранной области на основе доменной онтологии
* дополнение core AI-функций.

## Начало работы

1. Клонируем репо:
```
git clone https://github.com/ady1981/core-kbt.git
cd core-kbt
```
2. Задаем значения переменных среды в `.env` файле, например для DeepSeek:
```shell
DEVELOPMENT=1
HOST=127.0.0.1
PORT=5000
PYTHONUTF8=1
PYTHONIOENCODING=utf8
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
OPENAI_API_KEY=<DEEPSEEK_API_TOKEN>
AI_FUNC_API_TOKEN=<A_SECRET>
```
2. Запускаем сервер AI-функций:
```shell
./runner.sh -s kbt-core/ai_function_server.py
```
3. Допустим мы хотим узнать столицу России. Будем использовать готовую AI-функцию `generate_what_is` с [промптом](ai_functions/generate_what_is/prompt.md.j2) и [JSON-схемой ответа](ai_functions/generate_what_is/output_schema.yaml).
Вызываем AI-функцию с соответствующими входными параметрами `context`, `attribute` и `description`:
```shell
source .env
curl -X PUT "http://127.0.0.1:5000/ai-func/generate_what_is" \
  -H "Api-Token: $AI_FUNC_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "{
  \"context\": \"Geography\",
  \"attribute\": \"capital (in a shortest form)\",
  \"description\": \"of Russia\"
}"
```
Ответ:
```
{
  "result": {
    "final_answer": "Moscow",
    "notes": "Moscow has been the capital since the 15th century, with a brief interruption during the time of the Russian Empire when the capital was moved to Saint Petersburg.",
    "proof": "Moscow is the capital of Russia as recognized by the Constitution of the Russian Federation and is the political, economic, and cultural center of the country."
  }
}
```
