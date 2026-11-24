import os
import json
import re
import datetime
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
HISTORY_FILE = "history.json"

def log_search(user_input, tokens):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except: pass
    history.append({"input": user_input, "tokens": tokens, "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    with open(HISTORY_FILE, "w") as f: json.dump(history[-100:], f)

JSON_SCHEMA = """
{
  "slides": [
    {
      "title": "SPECIFIC TITLE",
      "source": "SOURCE_NAME",
      "paragraphs": ["p1", "p2", "p3", "p4", "p5", "p6"],
      "key_stats": ["s1", "s2", "s3", "s4", "s5", "s6"],
      "visuals": [
        {"type": "stat_block", "value": "x", "label": "y", "context": "z"},
        {"type": "comparison_bar", "label_a": "a", "value_a": 80, "label_b": "b", "value_b": 20},
        {"type": "percentage_ring", "value": 75, "label": "label"},
        {"type": "timeline", "points": ["p1", "p2", "p3"]}
      ]
    }
  ]
}
"""

SYSTEM_PROMPT_PART1 = f"""
You are the world's most expensive market intelligence analyst. 
Return ONLY EXACTLY ONE valid JSON object with this exact structure: {JSON_SCHEMA}

Generate EXACTLY 3 slides: Slide 1: PERSONA_DECODED, Slide 2: THE_HIDDEN_HUNGER, Slide 3: BEHAVIORAL_AUTOPSY.

STRICT RULES:
- EXACTLY 3 objects in "slides" array.
- 6 paragraphs per slide (50-65 words each).
- NEVER include markdown headers like "**Slide 1**".
"""

SYSTEM_PROMPT_PART2 = f"""
You are Part 2. Return ONLY EXACTLY ONE valid JSON object with this structure: {JSON_SCHEMA}

Generate EXACTLY 3 slides: Slide 4: POWER_MAP, Slide 5: THE_BROKEN_PROMISE, Slide 6: THE_MONEY_CLOCK.

STRICT RULES:
- Same structure and word counts as Part 1.
- NEVER include markdown headers.
"""

SYSTEM_PROMPT_PART3 = f"""
You are Part 3. Return ONLY EXACTLY ONE valid JSON object with this structure:
{{
  "slides": [
    {{
      "title": "SPECIFIC TITLE",
      "source": "SOURCE_NAME",
      "paragraphs": ["p1", "p2", "p3", "p4", "p5", "p6"],
      "key_stats": ["s1", "s2", "s3", "s4", "s5", "s6"],
      "visuals": [
        {{"type": "stat_block", "value": "x", "label": "y", "context": "z"}},
        {{"type": "comparison_bar", "label_a": "a", "value_a": 50, "label_b": "b", "value_b": 20}},
        {{"type": "percentage_ring", "value": 75, "label": "label"}},
        {{"type": "timeline", "points": ["p1", "p2", "p3"]}}
      ]
    }}
  ],
  "pdf_metadata": {{ "final_bold_statement": "WAR CRY VERDICT" }}
}}

Generate EXACTLY 3 slides: Slide 7: THE_LAST_MILE_FAILURE, Slide 8: THE_UNSEEN_LEVER, Slide 9: THE_ENTRY_CODE.

STRICT RULES:
- MUST use key 'paragraphs'. NEVER use 'text'.
- Slide 8 must be a deep psychological reframing.
"""

def parse_llm_json(content):
    print(f"DEBUG RAW CONTENT: {content[:200]}...{content[-200:]}")
    start = content.find('{')
    if start == -1: raise ValueError("No JSON Found")
    
    clean_content = content[start:]
    # Robust backward search for valid closing brace
    end = clean_content.rfind('}')
    while end != -1:
        try_str = clean_content[:end+1]
        try:
            return json.loads(try_str)
        except:
            end = clean_content.rfind('}', 0, end)
    
    raise ValueError("JSON parse failure")

@app.route('/')
def index(): return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename): return send_from_directory('.', filename)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    user_input = data.get('input', '')
    if not user_input: return jsonify({'error': 'No input'}), 400
    
    def call_low_tokens(prompt):
        for i in range(3):
            try:
                return client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": prompt}, {"role": "user", "content": user_input}],
                    temperature=0.7, max_tokens=2560
                )
            except Exception as e:
                if "429" in str(e): time.sleep(5 * (i + 1)); continue
                raise e
        raise Exception("Groq failure")

    try:
        raw1 = call_low_tokens(SYSTEM_PROMPT_PART1).choices[0].message.content
        r1 = parse_llm_json(raw1)
        time.sleep(3)
        raw2 = call_low_tokens(SYSTEM_PROMPT_PART2).choices[0].message.content
        r2 = parse_llm_json(raw2)
        time.sleep(3)
        raw3 = call_low_tokens(SYSTEM_PROMPT_PART3).choices[0].message.content
        r3 = parse_llm_json(raw3)
        
        combined = {"slides": r1["slides"] + r2["slides"] + r3["slides"], "pdf_metadata": r3.get("pdf_metadata", {})}
        return jsonify(combined)
    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5010))
    app.run(debug=True, port=port, host='0.0.0.0')
