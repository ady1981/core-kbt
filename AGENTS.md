# `core-kbt` Agent-Based Architecture

This document provides a comprehensive overview of the `core-kbt` project, its agent-based architecture, and instructions for development and usage.

## 1. Project Overview

The `core-kbt` (Knowledge Base Trajectory) project is a Python-based mini-framework for developing LLM-based applications. Its core principle is a **knowledge-base-driven approach**, where **AI Agents** intelligently evolve a version-controlled **Knowledge Base** to perform complex tasks.

### Key Technologies
*   **Backend:** Python, Flask
*   **Templating:** Jinja2
*   **Knowledge Representation:** RDFLib, Ontologies (YAML, JSON, Turtle)
*   **LLM Integration:** OpenAI API
*   **Dependency Management:** Poetry

## 2. Core Concepts

The architecture revolves around three main components: AI Agents, AI Functions, and the Knowledge Base.

### 2.1. AI Agents

AI Agents are the central actors in the system. Their primary role is to perform tasks by intelligently modifying the Knowledge Base. Each significant change an agent makes results in a new, qualitatively different state of the KB, which is versioned in a separate Git branch. This allows for a "trajectory" of knowledge states to be created and evaluated.

### 2.2. AI Functions

AI Functions are the tools that AI Agents use to interact with the world and modify the Knowledge Base. They are designed to be reusable, modular, and "intelligent" components with well-defined input and output schemas.

There are two ways to implement an AI Function:
1.  **Jinja2 Template:** A prompt template that can be executed by an LLM.
2.  **Python Module:** A Python function that can contain arbitrary logic, including calls to external APIs or other complex operations.

A Flask server exposes these functions through a RESTful API, handling authorization and dispatch.

### 2.3. Knowledge Base (KB)

The Knowledge Base is the structured repository of domain knowledge that agents operate on. It is stored as a hierarchy of YAML, JSON, or Turtle files, making it both human-readable and machine-processable.

The entire KB is managed under Git, allowing for robust versioning. Each branch can represent a different state of knowledge, enabling experiments and a clear audit trail of the agents' work.

## 3. System Architecture

The workflow is as follows:
1.  An **AI Agent** receives a high-level task.
2.  To accomplish the task, the agent invokes one or more **AI Functions** via the API.
3.  The AI Function executes, potentially calling an LLM or other services.
4.  The result is used to modify the **Knowledge Base**.
5.  The changes to the KB are committed to a new Git branch, creating a new, verifiable state of knowledge.

The final result of a task is selected from the various KB states based on a defined metric.

## 4. Getting Started

### 4.1. Prerequisites

*   Python 3.10+
*   Poetry
*   An OpenAI-compatible API key

### 4.2. Setup

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

### 4.3. Running the Server

Start the AI Function server using the provided script:
```bash
./runner.sh -s kbt-core/ai_function_server.py
```
The server will run on the host and port specified in your `.env` file (e.g., `127.0.0.1:5000`).

### 4.4. Testing

You can test an AI function with a `curl` request.
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

## 5. Development Guide

### 5.1. Creating AI Functions

You can extend the system by adding new AI Functions.

*   **Jinja2 Template:**
    1.  Create a new directory in `ai_function_templates/`.
    2.  Add a `prompt.md.j2` file for the prompt.
    3.  Add an `output_schema.yaml` to define the expected output structure.

*   **Python Module:**
    1.  Create a new Python module in `kbt-core/ai_function_impl/`.
    2.  The module must contain an `evaluate` function that takes the required arguments.

### 5.2. Working with the Knowledge Base

*   The KB is located in the `elementary/` directory.
*   Changes should be structured and follow the existing format (YAML, JSON, or Turtle).
*   All changes should be committed to Git to preserve the knowledge trajectory.

### 5.3. Project Conventions

*   **Dependencies:** Managed with Poetry in `pyproject.toml`.
*   **Configuration:** All configuration is handled via environment variables loaded from `.env`.
*   **Code Style:** Follow the existing patterns in the codebase.
