"""
STC ALGO V5 - Step 2: Context Refiner (Intent Clustering)
"""

import sys
import json
from utils import call_llm, web_search, extract_json, validate_pipeline_data, logger
from config import Config

def refine_intent(step1_data):
    """
    Gathers real-world context for the analytical bases and refines the intent.
    """
    analytical_bases = step1_data.get("analytical_bases", [])
    search_context = []

    # Gather evidence for each analytical base
    for query in analytical_bases:
        logger.info(f"Searching context for: {query}")
        results = web_search(query)
        search_context.extend(results)

    # Prepare LLM prompt
    system_prompt = f"""
You are the Context Refiner of the STC ALGO V5 system. 
Analyze the original intent and the gathered search context to generate a Refined Intent Cluster.

V5_FRAMEWORK_ENGINE:
{Config.V5_FRAMEWORK_ENGINE}

ORIGINAL INTENT DATA:
{json.dumps(step1_data, indent=2)}

SEARCH EVIDENCE:
{json.dumps(search_context[:15], indent=2)} # Limiting context for prompt size

Your output must be a VALID JSON object with these fields:
1. core_subject: The central theme of the cluster.
2. behavioural_tension: The Layer 3 insight (the friction driving the behavior).
3. domain_boundary: Where this behavior starts and ends.
4. location_context: Geographic or digital space where this is most prevalent.
5. surface_thread: The visible manifestation of this deeper cluster.
"""

    schema = {
        "core_subject": str,
        "behavioural_tension": str,
        "domain_boundary": str,
        "location_context": str,
        "surface_thread": str
    }

    attempts = 0
    while attempts < Config.MAX_RETRIES:
        raw_response = call_llm(system_prompt, "Refine the cluster context.")
        
        if raw_response == "SIMULATED_LLM_RESPONSE":
            data = {
                "core_subject": "Modern Micro-Subscription Churn",
                "behavioural_tension": "The gap between perceived premium value and the friction of habit formation.",
                "domain_boundary": "Post-purchase friction in Gen-Z lifestyle services.",
                "location_context": "Metropolitan tier-1/2 digital economies.",
                "surface_thread": "Rapid abandonment of high-ticket recurring costs in favor of flexible transactional use."
            }
        else:
            data = extract_json(raw_response)

        if data:
            validation = validate_pipeline_data(data, schema)
            if validation["valid"]:
                # Merge with previous step data for lineage
                data["step1_lineage"] = step1_data
                return data

        attempts += 1
    return None

if __name__ == "__main__":
    try:
        # Read from stdin if piped, else from argv
        if not sys.stdin.isatty():
            input_data = json.load(sys.stdin)
        else:
            input_data = json.loads(sys.argv[1])
        
        result = refine_intent(input_data)
        if result:
            print(json.dumps(result, indent=2))
        else:
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error in Step 2: {str(e)}")
        sys.exit(1)
