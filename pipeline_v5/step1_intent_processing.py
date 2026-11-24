"""
STC ALGO V5 - Step 1: Intent Processing Engine

Integration Note:
This script acts as the primary analytical entry point. In the final system, 
it will be invoked via a Flask route (e.g., /api/analyze) which captures 
user input from the index.html frontend and passes it here for processing.
"""

import sys
import json
from utils import call_llm, extract_json, validate_pipeline_data, logger
from config import Config

def process_intent(query):
    """
    Decomposes the raw market query into structured behavioral intelligence.
    """
    
    # Define the system prompt with the V5 Framework Engine
    system_prompt = f"""
You are the Intent Processing Engine of the STC ALGO V5 system.
Apply the V5_FRAMEWORK to decompose this raw input. Do not summarize.
You must perform a Semantic Decomposition.

V5_FRAMEWORK_ENGINE:
{Config.V5_FRAMEWORK_ENGINE}

Your output must be a VALID JSON object with the following fields:
1. clean_input: The query stripped of fluff but with intent sharpened.
2. domain: The specific behavioral space (e.g., "Aspirational Tier-2 Fitness").
3. actor_profile: A deep description of the human involved using V5 segmentation (Disciplined vs. Impulsive).
4. temporal_markers: Identify where the query sits on the Day 0–60+ churn curve.
5. hidden_assumptions: A list of 5 things the user is assuming that might be wrong.
6. analytical_bases: A list of 6 distinct research paths. Each must be a targeted search query designed to find measurable data.
7. hypotheses: 4 non-obvious theories about why the behavior exists using the 'perceived-vs-actual attribution gap' logic.
"""

    # Schema for validation
    schema = {
        "clean_input": str,
        "domain": str,
        "actor_profile": str,
        "temporal_markers": str,
        "hidden_assumptions": list,
        "analytical_bases": list,
        "hypotheses": list
    }

    attempts = 0
    max_pipeline_retries = Config.MAX_RETRIES

    while attempts < max_pipeline_retries:
        logger.info(f"Pipeline Attempt {attempts + 1} for Intent Processing")
        
        # Call LLM with cascading fallback
        raw_response = call_llm(system_prompt, query)
        
        if not raw_response:
            logger.error("LLM failed to return a response.")
            attempts += 1
            continue

        # Extract JSON from response
        # Since call_llm is currently returning "SIMULATED_LLM_RESPONSE", 
        # I'll add a mock return for demonstration if it's the simulation.
        if raw_response == "SIMULATED_LLM_RESPONSE":
            data = {
                "clean_input": f"Optimized version of: {query}",
                "domain": "Target Market Segment - Alpha",
                "actor_profile": "Disciplined consumer with impulsive micro-transactions.",
                "temporal_markers": "Day 30 (Doubt Phase)",
                "hidden_assumptions": ["Assumes constant growth", "Ignore churn", "Underestimates friction", "Assumes high intent", "Assumes low competition"],
                "analytical_bases": [
                    "Query 1: Industry benchmarks for X",
                    "Query 2: Consumer spend in Y",
                    "Query 3: Churn rates in Z",
                    "Query 4: Market entry barriers A",
                    "Query 5: Demographic shifts B",
                    "Query 6: Technology adoption C"
                ],
                "hypotheses": ["Theory 1: Gap in A", "Theory 2: Gap in B", "Theory 3: Gap in C", "Theory 4: Gap in D"]
            }
        else:
            data = extract_json(raw_response)

        if data:
            # Check length of 'analytical_bases' as required
            if len(data.get("analytical_bases", [])) < 6:
                logger.warning("Fewer than 6 analytical bases found. Triggering regeneration.")
                attempts += 1
                continue

            # Validate the structure and content
            validation = validate_pipeline_data(data, schema)
            if validation["valid"]:
                return data
            else:
                logger.warning(f"Validation failed: {validation['reason']}. Retrying...")
        
        attempts += 1
        
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No query provided. Please pass a market query string as an argument."}))
        sys.exit(1)

    market_query = sys.argv[1]
    result = process_intent(market_query)
    
    if result:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps({"error": "Failed to process intent after multiple attempts."}))
