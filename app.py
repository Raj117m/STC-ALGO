import os
import json
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
HISTORY_FILE = "history.json"

import datetime
def log_search(user_input, tokens):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except: pass
    
    history.append({
        "input": user_input,
        "tokens": tokens,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-100:], f) # Keep last 100

SYSTEM_PROMPT = """
You are a visceral behavioral deconstruction engine.
Return ONLY valid JSON. No preamble. No markdown fences.

Return this exact structure:

{
  "slides": [
    {
      "title": "A UNIQUE, VISCERAL TITLE IN CAPS",
      "source": "NARRATIVE_SOURCE",
      "paragraphs": ["p1", "p2", "p3", "p4", "p5", "p6"]
    }
  ],
  "pdf_metadata": {
    "final_bold_statement": "One powerful, aggressive 15-20 word strategic verdict."
  }
}

The slides array must have EXACTLY 9 slides in this order:

Slide 1 - PERSONA_VOICE: Values declared by the subject.
Slide 2 - PERSONA_VOICE: Hidden emotional hunger/fear.
Slide 3 - PERSONA_VOICE: Concrete behavioral contradictions.
Slide 4 - MARKET_STRUCTURE: Power dynamics and profit motives.
Slide 5 - MARKET_STRUCTURE: Systemic failures and traps.
Slide 6 - MARKET_STRUCTURE: Measured cycles and markers.
Slide 7 - INTERSECTION_LOG: Points of maximum friction.
Slide 8 - INTERSECTION_LOG: Non-obvious control mechanisms.
Slide 9 - CONVERGENCE: The final tactical execution plan.

RULES:
- DO NOT USE PLACEHOLDER TITLES. Generate aggressive, relevant titles.
- Every slide must have EXACTLY 6 paragraphs.
- Each paragraph must be 45-60 words.
- MANDATORY: Every paragraph must include at least one quantified behavioral statistic (e.g. "84% shift", "12s latency").
- Use <span class='highlight'>...</span> for stats.
- Return ONLY valid JSON. No preamble. No markdown.
"""

def parse_llm_json(content):
    # 1. Strip fences
    content = re.sub(r'```(?:json)?\s*|\s*```', '', content).strip()
    
    # 2. Extract object
    start = content.find('{')
    end = content.rfind('}')
    if start == -1 or end == -1:
        raise ValueError("No JSON object found")
    content = content[start:end+1]
    
    # 3. Handle raw newlines inside string values
    # We look for newlines that are not preceded by a quote and colon (start of value) 
    # and not followed by a quote and comma/brace (end of value).
    # A simpler way: find all string values and replace their raw newlines.
    
    # This regex tries to find text between double quotes.
    # It's not perfect but helps with LLM output.
    def replace_newlines(match):
        return match.group(0).replace('\n', '\\n').replace('\r', '\\r')
    
    # Replace newlines only inside what looks like "key": "value"
    # content = re.sub(r'":\s*"([^"]*)"', replace_newlines, content)
    
    # Actually, a more robust way is to replace ALL newlines that are NOT 
    # followed by a key pattern or a closing brace.
    # But let's try just allowing the LLM to get it right first with the prompt.
    
    return json.loads(content)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    user_input = data.get("input", "")
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0.2,
            max_tokens=4096,
        )
        
        raw = response.choices[0].message.content
        
        # Strip markdown fences if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()
        
        # Parse JSON
        result = json.loads(raw)
        
        # Log usage
        usage = getattr(response, 'usage', None)
        total_tokens = usage.total_tokens if usage else 0
        log_search(user_input, total_tokens)
        
        return jsonify(result)

    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Raw output: {raw}")
        return jsonify({"error": "JSON parse failed", "raw": raw}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/history')
def get_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route('/admin/stats')
def get_stats():
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except: pass
    return jsonify(history)

if __name__ == '__main__':
    app.run(debug=True, port=5010)
