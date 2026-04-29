# `core-kbt` Architecture

This document provides a comprehensive overview of the `core-kbt` project, its agent-based architecture, and instructions for development and usage.

## 1. Project Overview

The `core-kbt` (Knowledge Base Trajectory) project is a Python-based mini-framework for developing LLM-based applications. Its core principle is a **knowledge-base-driven approach**, where **AI Agents** intelligently evolve a version-controlled **Knowledge Base** to perform complex tasks.

### Key Technologies
*   **Backend:** Python, Flask
*   **Templating:** Jinja2
*   **LLM Integration:** OpenAI-compatible API
*   **Dependency Management:** Poetry

## 2. Core Concepts

The architecture revolves around two main components: AI Functions, and the Knowledge Base.

### 2.1. AI Functions

AI Functions are the tools to use to interact with the world and modify the Knowledge Base. They are designed to be reusable, modular, and "intelligent" components with well-defined input and output schemas.

There are two ways to implement an AI Function:
1.  **Jinja2 Template:** A prompt template that can be executed by an LLM.
2.  **Python Module:** A Python function that can contain arbitrary logic, including calls to external APIs or other complex operations.

A Flask server exposes these functions through a RESTful API, handling authorization and dispatch.

### 2.2. Knowledge Base (KB)

The Knowledge Base is the structured repository of domain knowledge that agents operate on. It is stored as a hierarchy of YAML, JSON, or Turtle files, making it both human-readable and machine-processable.

The entire KB is managed under Git, allowing for robust versioning. Each branch can represent a different state of knowledge, enabling experiments and a clear audit trail of the agents' work.

The final result of a task is selected from the various KB states based on a defined metric.

## 3. Getting Started

### 3.1. Prerequisites

*   Python 3.10+
*   Poetry
*   An OpenAI-compatible API key

### 3.2. Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ady1981/core-kbt.git
    cd core-kbt
    ```

2.  **Create a `.env` file:**
    Copy the example file and add your credentials.
    ```bash
    cp .env.example .env
    ```
    You must set `OPENAI_BASE_URL`, `OPENAI_MODEL`, `OPENAI_API_KEY`, and a secret `AI_FUNC_API_TOKEN`.

### 3.3. Running the Server

Start the AI Function server using the provided script:
```bash
./runner.sh -s kbt-core/ai_function_server.py
```
The server will run on the host and port specified in your `.env` file (e.g., `127.0.0.1:5000`).

### 3.4. Testing

You can test an AI function with a `curl` request.
```bash
source .env
curl -X PUT "http://127.0.0.1:5001/ai-func/generate" \
  -H "Api-Token: $AI_FUNC_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "{
  \"target_specification\": \"target_description: What is Capital of Russia?\"
}"
```