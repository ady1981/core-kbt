#!/bin/bash

# --- Configuration ---
# Set the path to your Poetry project directory.
# If left empty, the script will assume the current directory is the project root.
POETRY_PROJECT_DIR=""

# Name of the Python script to execute (e.g., "main.py", "my_app/run.py")
PYTHON_SCRIPT_TO_RUN=""

# Optional arguments to pass to the Python script
PYTHON_SCRIPT_ARGS=""

# --- Script Logic ---

# Function to display usage information
usage() {
    echo "Usage: $0 -s <python_script_path> [-d <project_directory>] [-a <script_arguments>]"
    echo ""
    echo "  -s <python_script_path> : Required. Path to the Python script to execute (e.g., 'main.py', 'src/app.py')."
    echo "  -d <project_directory>  : Optional. Path to the Poetry project directory. Defaults to current directory."
    echo "  -a <script_arguments>   : Optional. Arguments to pass to the Python script (e.g., '--verbose --config=dev.ini')."
    echo "  -h                      : Display this help message."
    echo ""
    echo "Example: $0 -s kbt-core/ai_function_server.py -d $PWD -a extra-arg"
    exit 1
}

# Parse command-line arguments
while getopts "s:d:a:h" opt; do
    case ${opt} in
        s )
            PYTHON_SCRIPT_TO_RUN=$OPTARG
            ;;
        d )
            POETRY_PROJECT_DIR=$OPTARG
            ;;
        a )
            PYTHON_SCRIPT_ARGS=$OPTARG
            ;;
        h )
            usage
            ;;
        \? )
            echo "Invalid option: -$OPTARG" >&2
            usage
            ;;
    esac
done
shift $((OPTIND -1))

# Validate required arguments
if [ -z "$PYTHON_SCRIPT_TO_RUN" ]; then
    echo "Error: Python script path (-s) is required."
    usage
fi

# Determine the project directory
if [ -z "$POETRY_PROJECT_DIR" ]; then
    POETRY_PROJECT_DIR=$(pwd)
    echo "No project directory specified. Assuming current directory: $POETRY_PROJECT_DIR"
else
    echo "Using specified project directory: $POETRY_PROJECT_DIR"
fi

# Check if the project directory exists
if [ ! -d "$POETRY_PROJECT_DIR" ]; then
    echo "Error: Project directory '$POETRY_PROJECT_DIR' does not exist."
    exit 1
fi

# Navigate to the Poetry project directory
echo "Changing directory to $POETRY_PROJECT_DIR..."
cd "$POETRY_PROJECT_DIR" || { echo "Error: Could not change to directory $POETRY_PROJECT_DIR"; exit 1; }

# --- Dependency Management ---

echo "Checking for Poetry installation..."
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed or not in your PATH."
    echo "Please install Poetry: https://python-poetry.org/docs/#installation"
    exit 1
fi

if ! poetry install --no-root --sync --no-interaction; then
    echo "Error: Failed to install dependencies. Please check your pyproject.toml and network connection."
    exit 1
fi

# --- Python Script Execution ---
poetry run python "$PYTHON_SCRIPT_TO_RUN" $PYTHON_SCRIPT_ARGS
