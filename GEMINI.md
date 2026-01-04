# GEMINI.md

This file provides a comprehensive overview of the `core-kbt` project for the Gemini CLI.

## Project Overview

The `core-kbt` (Knowledge Base Trajectory) project is a Python-based mini-framework for developing LLM-based applications. It emphasizes a knowledge-base-driven approach, where prompts are optimized by refining the context from a domain knowledge base.

**Key Technologies:**

*   **Backend:** Python, Flask
*   **Templating:** Jinja2
*   **Data/Configuration:** YAML, JSON
*   **Knowledge Representation:** RDFLib, Ontologies
*   **LLM Integration:** OpenAI API
*   **Dependency Management:** Poetry

**Architecture:**

The project is conceived around the concept of "AI Functions", "AI agents" and "knowledge base evolution".

"AI Function" is reusable, modular "intelligent" function with defined input and output schemas. These functions can be either Jinja2 templates or Python modules.

The knowledge base is stored in a structured hierarchy of YAML, JSON or Turtle files, which can be versioned with Git.
The changes of knowledge base will be performed by "intelligent" agents (AI agents) and each qualitatively different state of the knowledge base will be in the corresponding Git branch. The final result of a primary "task" should be selected in these knowledge base states via corresponding metric.

A Flask server provides a RESTful API for listing and executing these AI Functions. The server handles authorization and dynamically dispatches requests to the appropriate function evaluator based on its type.

## Building and Running

### Prerequisites

*   Python 3.10+
*   Poetry
*   An OpenAI-compatible API key

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ady1981/core-kbt.git
    cd core-kbt
    ```

2.  **Create a `.env` file:**
    Copy the `.env.example` file to `.env` and fill in the required environment variables:
    ```bash
    cp .env.example .env
    ```
    At a minimum, you will need to set:
    *   `OPENAI_BASE_URL`
    *   `OPENAI_MODEL`
    *   `OPENAI_API_KEY`
    *   `AI_FUNC_API_TOKEN` (a secret of your choice)

### Running the Server

The AI function server can be started using the `runner.sh` script:

```bash
./runner.sh -s kbt-core/ai_function_server.py
```

This will start the Flask server on the host and port specified in your `.env` file (defaults to `127.0.0.1:5000`).

### Testing

You can test the server by sending a `curl` request. For example, to use the `generate_what_is` AI function:

```bash
source .env
curl -X PUT "http://127.0.0.1:5000/ai-func/generate_what_is" \
  -H "Api-Token: $AI_FUNC_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
  "context": "Geography",
  "attribute": "capital (in a shortest form)",
  "attribute_description": "of Russia"
}'
```

## Development Conventions

*   **Dependency Management:** Dependencies are managed with Poetry and are defined in the `pyproject.toml` file.
*   **AI Functions:** New AI functions can be added in two ways:
    1.  **Jinja2 Template:** Create a new directory in `ai_function_templates` with a `prompt.md.j2` file and an `output_schema.yaml`.
    2.  **Python Module:** Create a new Python module in the `kbt-core/ai_function_impl` directory. The module must contain an `evaluate` function.
*   **Environment Variables:** All configuration is done through environment variables, loaded from a `.env` file.
*   **Code Style:** The codebase is reasonably well-structured. New code should follow the existing patterns.
*   **Knowledge Base:** The knowledge base is stored in the `elementary` directory. Changes to the knowledge base should be committed to Git.
