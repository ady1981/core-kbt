import sys
import traceback

from dotenv import load_dotenv
import os
import json

from common import log_str

load_dotenv()

from flask import Flask, request, jsonify

from ai_function_template import evaluate

app = Flask(__name__)

MAX_LOGGING_LEN = 512
API_TOKEN = os.getenv('AI_FUNC_API_TOKEN')


def is_authorized(request):
    return request.headers.get('api-token') == API_TOKEN


@app.route('/state/list-ai-functions', methods=['PUT'])
def execute():
    if not is_authorized(request):
        return jsonify({"error": "Not authorized"}), 403
    return jsonify({'result': os.listdir('ai_functions')}), 200


@app.route('/ai-func/<function_name>', methods=['PUT'])
def execute_function(function_name):
    if not is_authorized(request):
        return jsonify({"error": "Not authorized"}), 403

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    try:
        input_data = request.json
    except Exception as e:
        log_str('--- Invalid JSON format:')
        log_str(traceback.format_exc())
        return jsonify({"error": f"Invalid JSON format: {e}"}), 400

    if not isinstance(input_data, dict):
        return jsonify({"error": "JSON input must be a dictionary of arguments."}), 400

    # Execute the function with the provided data
    try:
        result = evaluate(function_name, input_data)
        return jsonify({'result': result}), 200
    except Exception as e:
        log_str('--- Unknown error:')
        log_str(traceback.format_exc())
        return jsonify({"error": f"{e}"}), 500


# --- Run the Flask app ---
if __name__ == '__main__':
    # For development, set debug=True to get detailed error messages
    # In production, you'd use a production-ready WSGI server like Gunicorn or uWSGI
    HOST = os.getenv('HOST', '0.0.0.0')
    DEBUG = bool(os.getenv('DEVELOPMENT', ''))
    PORT = int(os.getenv('PORT', ''))
    log_str(f'--- OPENAI_BASE_URL: "{os.getenv("OPENAI_BASE_URL")}"')
    if not API_TOKEN:
        log_str('invalid-api-token')
        exit(1)
    app.run(host=HOST, debug=DEBUG, port=PORT)
