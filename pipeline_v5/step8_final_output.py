"""
STC ALGO V5 - Step 8: Executive Briefing (Final Output Engine)
"""

import sys
import json
from utils import call_llm, extract_json, validate_pipeline_data, logger
from config import Config

def generate_report(step7_data):
    """
    Synthesizes a high-end intelligence report from the refined cluster 
    and signatures.
    """
    step6_data = step7_data.get("step6_lineage", {})
    
    # System prompt for final synthesis
    system_prompt = f"""
You are the Executive Analysis Engine of the STC ALGO V5 system.
Synthesize a high-end intelligence report for the provided refined cluster and signatures.

V5_FRAMEWORK_ENGINE:
{Config.V5_FRAMEWORK_ENGINE}

REFINED CLUSTER:
{json.dumps(step7_data.get("updated_intent_cluster", {}), indent=2)}

BEHAVIOURAL SIGNATURES:
{json.dumps(step6_data.get("signatures", []), indent=2)}

INSTRUCTIONS:
1. Explain the structural hidden mechanisms causing the behavior.
2. ABSOLUTE BAN on system jargon (CE, TF, Loop, Cluster, CE/TF/Refined).
3. NO HEDGING: Do not use words like 'may', 'might', 'suggests', 'likely'. 
4. Asserts truth. Be professional, non-obvious, and high-impact.

Your output must be a VALID JSON object with:
1. behavioural_truth: A single, sharp paragraph defining the core invisible force driving the market.
2. key_insights: A list of EXACTLY 6 specific findings with inline data/stats (each must be 30+ words).
3. opportunity_gaps: A list of 5 market gaps caused by structural failures, explaining why they haven't been filled (each must be 30+ words).
4. recommended_directions: A list of 5 strategic paths, each split into 'MVP' (Immediate action) and 'Asymmetric' (Long-term moat) versions (each path total must be 40+ words).
"""

    schema = {
        "behavioural_truth": str,
        "key_insights": list,
        "opportunity_gaps": list,
        "recommended_directions": list
    }

    attempts = 0
    while attempts < Config.MAX_RETRIES:
        raw_response = call_llm(system_prompt, "Synthesize final report.")
        
        if raw_response == "SIMULATED_LLM_RESPONSE":
            data = {
                "behavioural_truth": "The market is governed by a radical shift where aspirational signaling has decoupled from traditional economic capacity, turning premium access into a mandatory social survival utility rather than a discretionary luxury.",
                "key_insights": [
                    "Urban consumers in developing economies allocate 25% of their net disposable income to status-bearing fitness services to offset the psychological depletion of high-density living conditions.",
                    "The attrition rate for traditional gyms is currently 40% higher than for boutique micro-studios that offer localized community validation and hyper-specific performance tracking data.",
                    "Digital fitness participation has increased by 115% among individuals earning below the national median income, driven by the perceived attribution gap between cost and social mobility.",
                    "Quick-commerce penetration into the protein supplement market reveals that 65% of premium fitness users prefer 'just-in-time' consumption over cost-effective bulk purchasing habits effectively.",
                    "VC incentive misalignment has flooded the market with subsidized memberships that create a false sense of demand while eroding the long-term moat of established legacy institutions.",
                    "Behavioral data confirms that signal-without-habit manifests in a 3:1 ratio where social media proof precedes actual physical participation in high-expenditure fitness activities regularly."
                ],
                "opportunity_gaps": [
                    "The 'Aspirational Credit' gap remains unfilled because traditional lenders fail to recognize fitness as a career-advancing social investment for younger metropolitan demographics today.",
                    "Localized micro-communities are ignored by large-scale wellness platforms that prioritize global scalability over the essential high-trust physical interaction needed for sustained behavioral change.",
                    "Data-driven motivation layers are currently siloed within individual apps, leaving a structural failure in cross-platform performance synthesis that could validate a user's total lifestyle ecosystem.",
                    "The 'Time-Poor Premium' segment lack services that integrate seamless transition from workspace to workout, creating a friction point that consistently triggers the 60-day abandonment curve.",
                    "Hybridized nutritional and physical planning remains fragmented because of regulatory silos, preventing the emergence of a total-body operating system for the urban striver class."
                ],
                "recommended_directions": [
                    {
                        "label": "Omni-Channel Status Integration",
                        "content": "MVP: Launch a digital badge system that integrates workout proof directly into professional networking platforms. Asymmetric: Build an exclusive biometric-gated physical network where membership is verified by sustained metabolic performance rather than recurring monthly financial payments."
                    },
                    {
                        "label": "The Fractional Premium Model",
                        "content": "MVP: Offer pay-per-use access to high-end equipment via existing residential concierge services instantly. Asymmetric: Establish a decentralized ownership model for neighborhood fitness hubs that allows users to earn equity through consistent physical participation and community coaching."
                    },
                    {
                        "label": "Predictive Burnout Prevention",
                        "content": "MVP: Implement a simple AI-driven scheduling tool that automatically pauses subscriptions during high-stress corporate windows. Asymmetric: Develop a deep-learning behavioral engine that predicts abandonment 14 days in advance and proactively re-calibrates the user's social incentives to maintain habit formation."
                    },
                    {
                        "label": "Aspirational Finance Products",
                        "content": "MVP: Create a 'Fitness First' credit card that offers higher reward tiers for biometric performance milestones. Asymmetric: Partner with insurance providers to offer underwritten health-premium discounts based on verified, impossible-to-fake activity data from the STC ALGO network."
                    },
                    {
                        "label": "The Modular Urban Gym",
                        "content": "MVP: Deploy shipping-container-based high-end gyms in under-served corporate parking zones for immediate local access. Asymmetric: Engineer a network of adaptive urban pods that use augmented reality to transform any public space into a private, high-status training environment instantly."
                    }
                ]
            }
        else:
            data = extract_json(raw_response)

        if data:
            validation = validate_pipeline_data(data, schema)
            if validation["valid"]:
                # Custom validation for Step 8 requirements
                if len(data["key_insights"]) == 6 and len(data["opportunity_gaps"]) == 5:
                    data["step7_lineage"] = step7_data
                    return data
                else:
                    logger.warning("Step 8 counts incorrect. Retrying...")

        attempts += 1
    return None

if __name__ == "__main__":
    try:
        if not sys.stdin.isatty():
            input_data = json.load(sys.stdin)
        else:
            input_data = json.loads(sys.argv[1])
        
        result = generate_report(input_data)
        if result:
            print(json.dumps(result, indent=2))
        else:
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error in Step 8: {str(e)}")
        sys.exit(1)
