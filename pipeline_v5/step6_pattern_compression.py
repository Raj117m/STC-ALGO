"""
STC ALGO V5 - Step 6: Signature Generation (Pattern Compression)
"""

import sys
import json
from utils import call_llm, extract_json, validate_pipeline_data, logger
from config import Config

def compress_patterns(step5_data):
    """
    Compresses tensions points into precise 'Behavioural Signatures' 
    representing Rules of Reality.
    """
    # System prompt for compression
    system_prompt = f"""
You are the Signature Generation Engine of the STC ALGO V5 system.
Compress the detected tension points into generalized 'Behavioural Signatures'.

V5_FRAMEWORK_ENGINE:
{Config.V5_FRAMEWORK_ENGINE}

TENSION DATA:
{json.dumps(step5_data.get("tension_points", []), indent=2)}

CONSTRAINT: A signature is a precise 'Rule of Reality' that explains why multiple tensions happen at once.

Your output must be a VALID JSON object with:
signatures: A list of 4 to 5 objects. Each must contain:
1. mechanism: A 40+ word description of the rule (e.g., 'The Trust-Latency Loop').
2. confidence_score: A float from 0.0 to 1.0 based on evidence strength.
3. contributing_tensions: A list of tension descriptions this signature explains.
4. v5_markers: Specific V5 framework markers this pattern hits (e.g., 'Moat Decay', 'VC Misalignment', 'Quick-commerce Distortion').
"""

    schema = {
        "signatures": list
    }

    attempts = 0
    while attempts < Config.MAX_RETRIES:
        raw_response = call_llm(system_prompt, "Generate behavioural signatures.")
        
        if raw_response == "SIMULATED_LLM_RESPONSE":
            data = {
                "signatures": [
                    {
                        "mechanism": "The Immediacy-Premium Paradox: Consumers claim price sensitivity regarding long-term commitments but consistently pay higher premiums for immediate, low-friction gratification via decentralized delivery platforms, demonstrating that the psychological cost of commitment outweighs the actual financial cost of the product.",
                        "confidence_score": 0.85,
                        "contributing_tensions": ["The user claims price sensitivity... yet they pay a higher effective per-cup price via quick-commerce."],
                        "v5_markers": ["Quick-commerce Distortion", "Signalling-without-habit"]
                    }
                ] * 4 # Mocking 4 valid entries
            }
        else:
            data = extract_json(raw_response)

        if data:
            validation = validate_pipeline_data(data, schema)
            if validation["valid"]:
                if 4 <= len(data.get("signatures", [])) <= 5:
                    # Validate mechanism word counts
                    valid_words = True
                    for sig in data["signatures"]:
                        if len(sig.get("mechanism", "").split()) < 40:
                            valid_words = False
                            break
                    
                    if valid_words:
                        data["step5_lineage"] = step5_data
                        return data
                    else:
                        logger.warning("Mechanism description under required 40 words.")
                else:
                    logger.warning("Did not get 4-5 signatures.")

        attempts += 1
    return None

if __name__ == "__main__":
    try:
        if not sys.stdin.isatty():
            input_data = json.load(sys.stdin)
        else:
            input_data = json.loads(sys.argv[1])
        
        result = compress_patterns(input_data)
        if result:
            print(json.dumps(result, indent=2))
        else:
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error in Step 6: {str(e)}")
        sys.exit(1)
