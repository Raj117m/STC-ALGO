import requests
import re
import json
import time
import logging
from config import Config

# Setup logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract_json(raw_response):
    """
    Finds the first and last { } or [ ] blocks using a robust regex pattern.
    Handles markdown code blocks and raw text.
    """
    try:
        # Regex to find block between { } or [ ]
        # Handles markdown blocks by searching for content inside brackets
        pattern = r'(\{.*\}|\[.*\])'
        match = re.search(pattern, raw_response, re.DOTALL)
        
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        
        # Fallback: if re.search fails, try cleaning markdown blocks manually
        cleaned = re.sub(r'```json|```', '', raw_response).strip()
        match = re.search(pattern, cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
            
        return None
    except Exception as e:
        logger.error(f"JSON Extraction Error: {str(e)}")
        return None

def web_search(query):
    """
    Uses duckduckgo-search to find information.
    Cleans output of HTML tags and non-ASCII characters.
    """
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            ddg_gen = ddgs.text(query, max_results=Config.SEARCH_LIMIT)
            for r in ddg_gen:
                # Clean HTML tags and non-ASCII
                title = re.sub(r'<[^>]+>', '', r.get('title', ''))
                snippet = re.sub(r'<[^>]+>', '', r.get('body', ''))
                title = title.encode('ascii', 'ignore').decode('ascii')
                snippet = snippet.encode('ascii', 'ignore').decode('ascii')
                
                results.append({
                    'title': title,
                    'snippet': snippet,
                    'source': r.get('href', '')
                })
        return results
    except Exception as e:
        logger.error(f"Web Search Error: {str(e)}")
        return []

def call_llm(system_prompt, user_input):
    """
    Implements a Cascading Fallback Loop.
    Rotates through BACKEND_PRIORITY on 429 or 500 errors.
    """
    backends = Config.BACKEND_PRIORITY.copy()
    current_backend_index = backends.index(Config.ACTIVE_BACKEND)
    
    priority_list = backends[current_backend_index:] + backends[:current_backend_index]
    
    for backend in priority_list:
        api_key = getattr(Config, f"{backend.upper()}_API_KEY", "")
        if "YOUR_" in api_key or not api_key:
            logger.warning(f"Skipping {backend} - key is placeholder or missing.")
            continue

        attempts = 0
        while attempts < Config.MAX_RETRIES:
            logger.info(f"Attempting {backend} (Attempt {attempts + 1})")
            try:
                if backend == 'gemini':
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
                    payload = {
                        "contents": [{"parts": [{"text": f"{system_prompt}\n\nUSER_INPUT: {user_input}"}]}]
                    }
                    resp = requests.post(url, json=payload, timeout=Config.REQUEST_TIMEOUT)
                
                elif backend == 'openai' or backend == 'groq':
                    url = "https://api.openai.com/v1/chat/completions" if backend == 'openai' else "https://api.groq.com/openai/v1/chat/completions"
                    payload = {
                        "model": "gpt-4o-mini" if backend == 'openai' else "llama-3.3-70b-versatile",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_input}
                        ],
                        "response_format": {"type": "json_object"} if backend == 'openai' else None
                    }
                    headers = {"Authorization": f"Bearer {api_key}"}
                    resp = requests.post(url, json=payload, headers=headers, timeout=Config.REQUEST_TIMEOUT)
                
                else:
                    # No real client for this backend yet. Only return placeholder text when
                    # simulation is switched on, so it is never passed off as a real result.
                    if not Config.SIMULATE:
                        logger.warning(f"No client for {backend}; skipping (set STC_SIMULATE=1 for placeholder output).")
                        break
                    logger.info(f"Using simulation for {backend}")
                    # Return a very long mock to satisfy word counts in all steps
                    mock_text = "This is a detailed simulation response designed to satisfy the high-density requirements of the STC ALGO V5 framework, ensuring that all word count validations for insights, mechanisms, and descriptions are successfully met across the entire intelligence pipeline execution process without triggering any re-processing flags or errors during the testing phase."
                    return json.dumps({
                        "mechanism": mock_text + " " + mock_text,
                        "behavioural_truth": mock_text,
                        "key_insights": [mock_text] * 6,
                        "opportunity_gaps": [mock_text] * 5,
                        "recommended_directions": [{"label": "Path", "content": mock_text}] * 5,
                        "tension_points": [{"tension_description": mock_text, "probe_question": mock_text}] * 6,
                        "signatures": [{"mechanism": mock_text + " " + mock_text}] * 5
                    })

                if resp.status_code == 200:
                    data = resp.json()
                    if backend == 'gemini':
                        return data['candidates'][0]['content']['parts'][0]['text']
                    else:
                        return data['choices'][0]['message']['content']
                
                elif resp.status_code in [429, 500, 503]:
                    logger.warning(f"Critical error {resp.status_code} on {backend}. Rotating.")
                    break # Break retry loop to try next backend
                else:
                    logger.error(f"{backend} failed with {resp.status_code}: {resp.text}")
                    attempts += 1
            
            except Exception as e:
                logger.error(f"Request error with {backend}: {str(e)}")
                attempts += 1
            
            if attempts < Config.MAX_RETRIES:
                time.sleep(1.5)
        
    logger.critical("All backends exhausted or failed.")
    return None

def validate_pipeline_data(data, schema):
    """
    Strict validator for pipeline data.
    Checks for missing keys and word counts (25+ for insights).
    """
    if not data or not isinstance(data, dict):
        return {"valid": False, "reprocess": True, "reason": "Invalid data format"}
    
    for key, expected_type in schema.items():
        if key not in data:
            logger.warning(f"Validation Failed: Missing key '{key}'")
            return {"valid": False, "reprocess": True, "reason": f"Missing key: {key}"}
        
        # Word count check for 'insights' or similar string fields
        if isinstance(data[key], str) and "insight" in key.lower():
            word_count = len(data[key].split())
            if word_count < 25:
                logger.warning(f"Validation Failed: '{key}' under word count ({word_count})")
                return {"valid": False, "reprocess": True, "reason": f"Low word count in {key}"}
                
    return {"valid": True, "reprocess": False, "data": data}

STATE_FILE = "pipeline_state.json"

def save_state(step: int, data: any, status: str):
    """Saves current state to persistence file atomically."""
    import os
    state = {
        "last_step": step,
        "status": status,
        "timestamp": time.time(),
        f"step_{step}_data": data
    }
    # Load existing state to preserve previous step data
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                current_state = json.load(f)
                state.update(current_state)
                # Update with current step
                state["last_step"] = step
                state["status"] = status
                state[f"step_{step}_data"] = data
        except:
            pass
            
    tmp_file = f"{STATE_FILE}.tmp"
    try:
        with open(tmp_file, 'w') as f:
            # Safely handle non-serializable objects with default=str
            json.dump(state, f, indent=2, default=str)
        # Atomic rename
        os.replace(tmp_file, STATE_FILE)
    except Exception as e:
        logger.error(f"Atomic Write Error: {str(e)}")
    
    print(f"STATUS: STEP_{step}_COMPLETE")

def load_state():
    """Loads state from persistence file safely."""
    import os
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"last_step": 0, "status": "INITIALIZING"}
