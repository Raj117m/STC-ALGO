"""
STC ALGO V5 - UI Bridge (app.py)
"""

import os
import json
import threading
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import run_pipeline

app = Flask(__name__)
CORS(app)

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)

# Ensure state file is clean on startup
if os.path.exists(run_pipeline.STATE_FILE):
    os.remove(run_pipeline.STATE_FILE)

@app.route('/')
def home():
    """Serve the V5 interface (pipeline_v5/index.html)."""
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/api/run', methods=['POST'])
def run_task():
    """Receives the query and triggers the pipeline in a background thread."""
    data = request.json
    query = data.get('input', '').strip() # index.html sends {input: txt}
    
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Reset state for a new run
    if os.path.exists(run_pipeline.STATE_FILE):
        os.remove(run_pipeline.STATE_FILE)

    task_id = str(uuid.uuid4())
    
    # Start pipeline in background
    def run_with_error_handling(q):
        try:
            run_pipeline.run_v5_pipeline(q)
        except Exception as e:
            from utils import save_state
            save_state(0, {"error": str(e)}, "FAILED")
            print(f"PIPELINE CRITICAL FAILURE: {str(e)}")

    thread = threading.Thread(target=run_with_error_handling, args=(query,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "message": "Pipeline started", 
        "status": "PIPELINE_START",
        "task_id": task_id
    })

@app.route('/api/status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Polling endpoint to track pipeline progress with deep resilience."""
    try:
        state = run_pipeline.load_state()
    except:
        return jsonify({"status": "INITIALIZING", "last_step": 0})
    
    if state.get("status") == "FAILED":
        return jsonify(state), 200

    # index.html expects 'step_data' object for mapping steps
    # Construct it if it's not present for compatibility
    if "step_data" not in state:
        state["step_data"] = {
            "step1": state.get("step_1_data"),
            "step2": state.get("step_2_data"),
            "step3": state.get("step_3_data"),
            "step4": state.get("step_4_data"),
            "step5": state.get("step_5_data"),
            "step6": state.get("step_6_data"),
            "step7": state.get("step_7_data"),
            "step8": state.get("step_8_data")
        }
    
    # If complete, set the 'result' field index.html expects
    if state.get("last_step") == 8:
        state["result"] = state.get("step_8_data")
        state["status"] = "complete"
    else:
        state["status"] = "running"
        state["status_line"] = f"Step {state.get('last_step', 0) + 1} processing..."

    return jsonify(state)

if __name__ == '__main__':
    # Explicit binding and debug mode for stability
    print("V5 ENGINE ONLINE: Open http://127.0.0.1:5005 in your browser.")
    app.run(host='127.0.0.1', port=5005, debug=True)
