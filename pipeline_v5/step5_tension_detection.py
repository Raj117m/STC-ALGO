"""
STC ALGO V5 - Step 5: Contradiction Finder (Tension Detection)
"""

import sys
import json
from utils import call_llm, extract_json, validate_pipeline_data, logger
from config import Config

def detect_tension(step4_data):
    """
    Identifies 'Near-Connections' where conscious beliefs (Step 3) 
    are undermined by tangible actions (Step 4).
    """
    step3_data = step4_data.get("step3_lineage", {})
    
    # Define the tension detection logic
    system_prompt = f"""
You are the Contradiction Finder of the STC ALGO V5 system.
Identify the 'Tension Points'—near-connections where what the cluster says is undermined by what they do.

V5_FRAMEWORK_ENGINE:
{Config.V5_FRAMEWORK_ENGINE}

CONSCIOUS EXPRESSIONS (What they say):
{json.dumps(step3_data.get("direct_expressions", []) + step3_data.get("indirect_expressions", []), indent=2)}

TANGIBLE FOOTPRINTS (What they do):
{json.dumps(step4_data.get("direct_layer", []) + step4_data.get("peripheral_layer", []), indent=2)}

CONSTRAINT: 
- Direct alignments are ignored. 
- Complete contradictions are ignored. 
- Find the 'Tension' where a specific behavior exists despite an opposing belief.

Your output must be a VALID JSON object with:
tension_points: A list of EXACTLY 6 objects. Each must contain:
1. conscious_expression: The specific CE being challenged.
2. tangible_footprint: The specific TF causing the friction.
3. tension_description: A 30+ word explanation of the hidden behavioral mechanism at play.
4. probe_question: A 25+ word targeted investigative question for further research.
"""

    schema = {
        "tension_points": list
    }

    attempts = 0
    while attempts < Config.MAX_RETRIES:
        raw_response = call_llm(system_prompt, "Detect behavioral tensions.")
        
        if raw_response == "SIMULATED_LLM_RESPONSE":
            data = {
                "tension_points": [
                    {
                        "conscious_expression": "I believe that traditional coffee subscriptions are far too expensive for the level of quality being delivered.",
                        "tangible_footprint": "Data from quick-commerce platforms shows a 60% increase in one-off premium coffee orders.",
                        "tension_description": "The user claims price sensitivity as the primary reason for cancellation, yet they are willing to pay a higher effective per-cup price via quick-commerce just for the sake of immediate gratification and freedom from commitment.",
                        "probe_question": "Does the perceived lack of quality in subscriptions stem from the product itself, or from the psychological burden of a recurring financial obligation that feels inconsistent with a fluid lifestyle?"
                    }
                ] * 6 # Mocking 6 identical but valid entries
            }
        else:
            data = extract_json(raw_response)

        if data:
            validation = validate_pipeline_data(data, schema)
            if validation["valid"]:
                if len(data.get("tension_points", [])) == 6:
                    # Validate word counts
                    valid_words = True
                    for tp in data["tension_points"]:
                        if len(tp.get("tension_description", "").split()) < 30 or \
                           len(tp.get("probe_question", "").split()) < 25:
                            valid_words = False
                            break
                    
                    if valid_words:
                        data["step4_lineage"] = step4_data
                        return data
                    else:
                        logger.warning("Tension description or probe question under required word count.")
                else:
                    logger.warning("Did not get exactly 6 tension points.")

        attempts += 1
    return None

if __name__ == "__main__":
    try:
        if not sys.stdin.isatty():
            input_data = json.load(sys.stdin)
        else:
            input_data = json.loads(sys.argv[1])
        
        result = detect_tension(input_data)
        if result:
            print(json.dumps(result, indent=2))
        else:
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error in Step 5: {str(e)}")
        sys.exit(1)
