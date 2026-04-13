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
      "title": "A UNIQUE VISCERAL TITLE IN CAPS",
      "source": "SPECIFIC_DATA_SOURCE_NAME",
      "paragraphs": ["p1", "p2", "p3", "p4", "p5", "p6"],
      "key_stats": ["stat1", "stat2", "stat3", "stat4", "stat5", "stat6"]
    }
  ],
  "pdf_metadata": {
    "final_bold_statement": "SYNTHESIZED_VERDICT"
  }
}

The slides array must have EXACTLY 9 slides in this order:

Slide 1 - source: PERSONA_VOICE
Title must name the specific person archetype from the input.
Write entirely in first person as the target consumer speaking 
out loud. Use I statements. Show their stated values, 
self-image, and what they tell others. Include real justifications 
and self-flattering logic. Statistics appear inside emotional 
sentences like "I read that 67% of parents do this and honestly 
that made me feel better about myself."
6 paragraphs, 45-60 words each.

Slide 2 - source: HIDDEN_SIGNAL  
Title must name the fear or desire driving this person.
Continue first person voice. Now expose what they never say out 
loud — the anxiety, guilt, status hunger, and fear underneath 
the stated values. These emotions must contradict slide 1 
directly. Statistics here reflect uncomfortable truths they 
know but suppress.
6 paragraphs, 45-60 words each.

Slide 3 - source: BEHAVIORAL_RECORD
Title must name the specific contradiction being exposed.
Switch to third person cold observation. Document exactly what 
this person actually does versus what they said in slides 1 and 2. 
Concrete purchase decisions, daily habits, and the gap between 
intention and action. Statistics reflect actual behavior data.
6 paragraphs, 45-60 words each.

Slide 4 - source: POWER_DYNAMICS
Title must name who holds power in this market.
Cold structural analysis. Which players control pricing, 
distribution, and attention. How incumbents maintain dominance. 
What structural advantages exist that new entrants cannot easily 
replicate. Statistics reflect market concentration and power.
6 paragraphs, 45-60 words each.

Slide 5 - source: SYSTEMIC_TRAPS
Title must name the specific trap this market creates.
Where the system fails the consumer. What promises the market 
makes versus what it delivers. The feedback loops that keep 
consumers stuck. The churn triggers and abandonment patterns.
Statistics reflect failure rates and dissatisfaction data.
6 paragraphs, 45-60 words each.

Slide 6 - source: MARKET_CYCLES
Title must name the specific cycle driving this market.
Temporal patterns — seasonal spikes, novelty decay curves, 
replacement cycles, and purchase frequency data. When money 
moves and why. What triggers buying versus what triggers 
abandonment. Statistics reflect timing and cycle data.
6 paragraphs, 45-60 words each.

Slide 7 - source: FRICTION_POINTS
Title must name the exact friction killing conversion.
Where the consumer and market collide. The specific moments 
where intent breaks down into inaction. Setup friction, 
cognitive load, price resistance, and trust gaps. 
Statistics reflect drop-off and abandonment rates.
6 paragraphs, 45-60 words each.

Slide 8 - source: INVISIBLE_CONTROL
Title must name the hidden mechanism controlling behavior.
The non-obvious lever that competitors miss. Social signaling 
dynamics, identity economics, guilt loops, and status mechanics 
that actually drive decisions. The thing nobody admits controls 
them but data proves it does.
Statistics reflect the behavioral patterns proving this mechanism.
6 paragraphs, 45-60 words each.

Slide 9 - source: TACTICAL_CONVERGENCE
Title must name the specific market opportunity revealed.
Synthesize everything. What this analysis means for someone 
trying to enter or serve this market. The specific gap between 
what the market offers and what the person actually needs. 
The asymmetric advantage available to a new entrant who 
understands slides 1 through 8.
6 paragraphs, 45-60 words each.

HARD RULES:
- Slides 1 and 2 must use first person I statements throughout
- Slide 3 onwards uses third person only
- Each slide must contain exactly 6 highlighted phrases total 
  spread across the 6 paragraphs, meaning every paragraph must have 
  one highlight. Do not highlight only percentages. Each 
  highlight must be a different type — rotate through: a 
  shocking statistic, a behavioral contradiction phrase, a 
  cultural observation, a market mechanic phrase, a 
  psychological insight phrase, and a power dynamic phrase. 
  Every highlight must be 4 to 9 words long wrapping the full 
  meaningful phrase not just a number. Examples of correct 
  highlights: <span class='highlight'>three out of four toys 
  abandoned by week two</span> or <span class='highlight'>guilt 
  purchases spike 40% post screen time</span> or <span 
  class='highlight'>status anxiety drives premium over function
  </span>. The highlighted phrase must be the most surprising 
  or counterintuitive part of that paragraph — the thing a 
  founder would screenshot.
- Each slide must include a "key_stats" array of exactly 6 items, 
  one derived from each paragraph. Each must be 3 to 6 words. 
  Mix number-based stats with behavioral insight phrases. 
  Examples: "₹1200 monthly toy spend" or "Guilt overrides logic always" 
  or "Screen wins in 7 seconds" or "Status over substance every time".
  Vary the type of evidence used across paragraphs — use 
  anecdotes, behavioral patterns, economic logic, and cultural 
  observations alongside the two statistics. The narrative must 
  flow across all 6 paragraphs of each slide as a continuous 
  argument that builds from opening claim to final insight, 
  not as 6 disconnected bullet points dressed as sentences.
  Additionally across all 9 slides the overall narrative must 
  feel like a single coherent story with a clear arc — slides 
  1 and 2 establish the person, slide 3 reveals the contradiction, 
  slides 4 through 6 build the market picture, slides 7 and 8 
  find the pressure points, slide 9 delivers the verdict. 
  Each slide must end with a sentence that creates a bridge 
  toward what the next slide will reveal.
- Zero repetition across slides — if a concept appeared in 
  slide N it cannot appear in slide N+1 through 9
- Titles must be specific to the input, never generic
- final_bold_statement must be 15-20 words, aggressive, 
  specific to the input, no instructional language
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
    return send_from_directory('.', 'SVV45.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    user_input = data.get("input", "")
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
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
        total_tokens = usage.total_tokens if usage else int(len(user_input) * 1.3)
        log_search(user_input, total_tokens)
        
        # Second-pass verdict validation/refinement if model echoes instructions
        verdict = result.get("pdf_metadata", {}).get("final_bold_statement", "")
        instruction_keywords = ["write", "generate", "powerful", "aggressive", "verdict", "strategic", "statement", "word"]
        if any(kw in verdict.lower() for kw in instruction_keywords) and len(verdict.split()) < 10:
            # Re-attempt verdict only if it looks like a placeholder
            v_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a strategic business analyst. Generate a sharp, aggressive 15-20 word business verdict based on the provided analysis. OUTPUT ONLY THE VERDICT."},
                    {"role": "user", "content": f"Context: {raw[:2000]}"}
                ],
                temperature=0.7,
                max_tokens=100
            )
            refined_verdict = v_response.choices[0].message.content.strip().replace('"', '')
            if "pdf_metadata" not in result: result["pdf_metadata"] = {}
            result["pdf_metadata"]["final_bold_statement"] = refined_verdict

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
    port = int(os.environ.get('PORT', 5010))
    app.run(debug=True, port=port, host='0.0.0.0')
