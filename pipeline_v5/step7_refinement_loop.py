"""
STC ALGO V5 - Step 7: Cluster Evolution (Refinement Loop)
"""

import sys
import json
from utils import call_llm, extract_json, validate_pipeline_data, logger
from config import Config

def evolve_cluster(step6_data):
    """
    Performs an Additive, Verificative, and Corrective update of the cluster 
    based on the discovered signatures.
    """
    # Step 6 has Step 5, which has Step 4, which has Step 3, which has Step 2
    step5_data = step6_data.get("step5_lineage", {})
    step4_data = step5_data.get("step4_lineage", {})
    step3_data = step4_data.get("step3_lineage", {})
    step2_data = step3_data.get("step2_lineage", {})
    
    # Original Cluster State (Combined Step 1 and Step 2 fields to make 8)
    original_cluster = {
        "clean_input": step2_data.get("step1_lineage", {}).get("clean_input"),
        "domain": step2_data.get("step1_lineage", {}).get("domain"),
        "actor_profile": step2_data.get("step1_lineage", {}).get("actor_profile"),
        "core_subject": step2_data.get("core_subject"),
        "behavioural_tension": step2_data.get("behavioural_tension"),
        "domain_boundary": step2_data.get("domain_boundary"),
        "location_context": step2_data.get("location_context"),
        "surface_thread": step2_data.get("surface_thread")
    }

    system_prompt = f"""
You are the Cluster Evolution Engine of the STC ALGO V5 system.
Perform an Additive, Verificative, and Corrective update of the intent cluster using the new Behavioural Signatures.

V5_FRAMEWORK_ENGINE:
{Config.V5_FRAMEWORK_ENGINE}

ORIGINAL 8-FIELD CLUSTER:
{json.dumps(original_cluster, indent=2)}

BEHAVIOURAL SIGNATURES (The new Truth):
{json.dumps(step6_data.get("signatures", []), indent=2)}

Your goal is to rewrite the cluster so it reflects the deeper intelligence found.

Your output must be a VALID JSON object with:
1. updated_intent_cluster: The full 8-field cluster rewritten for depth.
   - clean_input
   - domain
   - actor_profile
   - core_subject
   - behavioural_tension
   - domain_boundary
   - location_context
   - surface_thread
2. delta_score: An integer (0-100) representing how much the system's understanding changed.
3. loop_signal: Either 'CONTINUE' (if delta > 30) or 'EXTRACT' (if converged).
"""

    schema = {
        "updated_intent_cluster": dict,
        "delta_score": int,
        "loop_signal": str
    }

    attempts = 0
    while attempts < Config.MAX_RETRIES:
        raw_response = call_llm(system_prompt, "Refine and evolve the cluster.")
        
        if raw_response == "SIMULATED_LLM_RESPONSE":
            data = {
                "updated_intent_cluster": original_cluster.copy(),
                "delta_score": 45,
                "loop_signal": "CONTINUE"
            }
            # Slightly modifying mock for 'evolution'
            data["updated_intent_cluster"]["behavioural_tension"] = "REFINED: " + original_cluster["behavioural_tension"]
        else:
            data = extract_json(raw_response)

        if data:
            validation = validate_pipeline_data(data, schema)
            if validation["valid"]:
                data["step6_lineage"] = step6_data
                return data

        attempts += 1
    return None

if __name__ == "__main__":
    try:
        if not sys.stdin.isatty():
            input_data = json.load(sys.stdin)
        else:
            input_data = json.loads(sys.argv[1])
        
        result = evolve_cluster(input_data)
        if result:
            print(json.dumps(result, indent=2))
        else:
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error in Step 7: {str(e)}")
        sys.exit(1)
