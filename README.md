## Project concept

The core-kbt project (kbt is an abbreviation for Knowledge Base Trajectory) is a mini-framework for developing LLM-based applications and domain knowledge bases, with examples of domain knowledge in the fields of knowledge representation, LLM and development tools.

The idea of the project can be presented from different sides:
* make convenient development tools for LLM-based applications
* develop and use an approach in which it is necessary to optimize the prompt for the task through optimizing the context, which is calculated from the task's knowledge base (domain knowledge base)
* the project is a development of the prompting-as-code idea.

### From the development convenience side

For practical application development using LLM:
* it is necessary to have an evident data model of what needs to be submitted to the LLM at the input and received at the output
* convenient ways to create new AI functions with predictable properties
* work with schema-less data, but with the fixation of both the JSON schema and the semantic schema (ontology), when necessary
* it is convenient to view and modify the data that is the context for LLM prompts
* cache responses from LLM
* parallelize requests to LLM providers with a controlled requests-per-second value.

### From the knowledge representation side

The new opportunities provided by GenAI technologies require new approaches to the representation of knowledge and programming methods.
LLM models have passed large amounts of textual information through generalized algorithms, and it should be expected that the LLM model's internal representation of the world will correspond to how people represent knowledge. The closest way to the human way of representing knowledge is the ontological representation. Therefore, it should be expected that the ontological representation will be the bridge between the "world of LLM representations" and the human representation of knowledge, which is necessary for the effective solution of practical problems.

It is proposed to use the following upper-level, more or less universal approach to solving the problem using LLM:
  * develop an upper-level ontology that should be convenient and understandable to LM and humans: [ontology-kb-classes/_all.yaml](elementary%2Fontology-kb-classes%2F_all.yaml)
  * develop typical domain ontologies that can be used for specific tasks (example: [comparison-kb-classes/_all.yaml](elementary%2Fcomparison-kb-classes%2F_all.yaml))
  * solve the problem in the following formulation:
    divide the information on the problem into the following blocks (`<I, as an LLM researcher, describe ...>`):
    * `<what I know>`: in the form of an ontology-based knowledge base
    * `<what I want to know>`: as a task in the knowledge base entities
    * `<what I want to generate>`: as a task in the knowledge base entities.

By gradually formulating tasks in the entities of the knowledge base and solving these tasks, we will gradually replenish the knowledge base. Until the entities that contain the answers for which this task was created appear in the knowledge base.

## What is the framework useful for?

* AI functions for fast creation and use of information processing functions via LLM, with a structured response
* database for YAML/JSON entities in file representation: fast and convenient data entry for AI processing, convenient editing of entities before and after AI processing
* if the JSON schema for YAML/JSON entities is not enough, to deepen knowledge to solve the problem, a consistent development of a domain ontology is needed for this task: you can use a ready-made top-level ontology as a base for creating a domain ontology: see [ontology-kb-classes/_all.yaml](elementary%2Fontology-kb-classes%2F_all.yaml)
* development of domain knowledge base trajectories: YAML/JSON entities and the state of the knowledge base are stored as files in git, which makes it convenient to mutate the values of knowledge base entities through git branching for further optimization and search for the best state of the knowledge base
* you can configure the CI pipeline for the git repository with the launch of the AI function server: as a result, you will get a convenient cycle of AI function development and domain knowledge base support
* persistent processes for convenient implementation of processing logic, processing planning, caching responses from external services and debugging.

## The framework features

* AI functions with structured responses (see [ai_functions](ai_functions)):
  * each AI function has a folder with a sample of the prompt and a JSON schema for the response:
    * j2 sample for the prompt (for example: [prompt.md.j2](ai_functions/list_best_tasks_for_llm_effectivess/prompt.md.j2))
    * the required JSON schema for the response (for example: [output_schema.yaml](ai_functions/list_best_tasks_for_llm_effectivess/output_schema.yaml))
  * there is an `evaluate` method for calling AI function: [ai_function.py](kbt-core/ai_function.py)
  * there is a server application for a dynamic API for calling any AI function:
    * server: [ai_function_server.py](kbt-core%2Fai_function_server.py)
    * the server authorizes all requests using an API token (a secret token)
    * client example: [ai_function_client.py](examples%2Fai_function_client.py)
* structured representation of YAML/JSON entities (see [elementary]):
  * each entity has a folder with entity elements represented as files
  * for ease of editing, the value for the entity field can be loaded from a file.
  * there is an API for working with entities: see [items_db.py](kbt-core/items_db.py)
* a ready-made version of a small upper-level basic ontology that is understandable to LLM and humans: [ontology-kb-classes/_all.yaml](elementary%2Fontology-kb-classes%2F_all.yaml)
* persistent processes for convenient implementation of processing logic, processing scheduling, caching responses from external services, and debugging (see  [processes](processes)):
  * a persistent process has input (input data for the process), state (current state of the process) and `status`: `initial` -> `running` -> (`terminated` | `error`)
  * processes can be started asynchronously in a set number of threads 
  * for each process, an input file in JSON is created with the input data for this process (in the folder [processes/input](processes/input)) and a process state file in JSON (in the folders [processes/by_status](processes/by_status)), into which the process can write its persistent state, and which records the result of the process when the process switches to `status=terminated` (folder [processes/by_status/terminated](processes/by_status/terminated))
  * the logic of the process is described in the process module file in the folder: [processes/implementation](processes/implementation)
  * the process determines how its ID is calculated in the `calc_input_id` method 
  * the creation of the process is described in the appropriate modules or scripts.

## Directions for the further development

* integration with Langfuse for traceability and quality assessment of prompts
* examples of prompt optimization through the trajectory of domain knowledge bases
* development of tools for conducting research in a specified field based on domain ontology
* addition of core AI functions.

## Getting started

1. clone repo:
```
git clone https://github.com/ady1981/core-kbt.git
cd core-kbt
```
2. set the values of environment variables in `.env` file, for example for DeepSeek:
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
2. launch the AI function server:
```shell
./runner.sh -s kbt-core/ai_function_server.py
```
3. For example, we want to find out the capital of Russia. We will use the ready-made AI function `generate_what_is` with [prompt](ai_functions/generate_what_is/prompt.md.j2) and [JSON response scheme](ai_functions/generate_what_is/output_schema.yaml). Call the AI function with the corresponding input parameters `context`, `qualifier` and `description`:
```shell
source .env
curl -X PUT "http://127.0.0.1:5000/ai-func/generate_what_is" \
  -H "Api-Token: $AI_FUNC_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "{
  \"context\": \"Geography\",
  \"qualifier\": \"capital (in a shortest form)\",
  \"description\": \"of Russia\"
}"
```
Response:
```
{
  "result": {
    "final_answer": "Moscow",
    "notes": "Moscow has been the capital since the 15th century, with a brief interruption during the time of the Russian Empire when the capital was moved to Saint Petersburg.",
    "proof": "Moscow is the capital of Russia as recognized by the Constitution of the Russian Federation and is the political, economic, and cultural center of the country."
  }
}
```
