"""
STC ALGO V5 - Step 4: Outcome Extraction (Tangible Footprints)
"""

import sys
import json
from utils import call_llm, web_search, extract_json, validate_pipeline_data, logger
from config import Config

def extract_outcomes(step3_data):
    """
    Finds measurable evidence of what is actually happening in the market.
    """
    # Step 3 data contains step2_lineage
    step2_data = step3_data.get("step2_lineage", {})
    analytical_bases = step2_data.get("step1_lineage", {}).get("analytical_bases", [])
    
    logger.info("Gathering measurable footprints and market data...")
    
    footprint_evidence = []
    for base in analytical_bases[:3]: # Using subset to manage search volume
        queries = [
            f"{base} measurable market data statistics",
            f"{base} case studies business failure success",
            f"{base} adjacent industry shifts trends"
        ]
        for q in queries:
            footprint_evidence.extend(web_search(q))

    system_prompt = f"""
You are the Outcome Extraction Engine of STC ALGO V5. 
Extract measurable, cold evidence of what is actually happening.

V5_FRAMEWORK_ENGINE:
{Config.V5_FRAMEWORK_ENGINE}

CONTEXT:
{json.dumps(step3_data, indent=2)}

RESEARCH EVIDENCE:
{json.dumps(footprint_evidence[:15], indent=2)}

Your output must be a VALID JSON object with:
1. direct_layer: Exactly 7 measurable outcomes with inline data/figures (each must be 25+ words).
2. peripheral_layer: Exactly 7 external forces or adjacent market movements (each must be 25+ words).
"""

    schema = {
        "direct_layer": list,
        "peripheral_layer": list
    }

    attempts = 0
    while attempts < Config.MAX_RETRIES:
        raw_response = call_llm(system_prompt, "Extract outcomes.")
        
        if raw_response == "SIMULATED_LLM_RESPONSE":
            data = {
                "direct_layer": [
                    "Market reports indicate a 34% drop in subscription retention for premium beverage services among the 18-25 demographic within the first ninety days of signup.",
                    "Venture capital funding for direct-to-consumer coffee brands has decreased by approximately $200 million over the last fiscal year, signaling a significant cooling of investor interest.",
                    "Average monthly churn rates for high-end lifestyle subscriptions have spiked to an all-time high of 12.5% in major metropolitan areas like New York and London.",
                    "The customer acquisition cost (CAC) for new subscribers has risen by 45% because of increased saturation and diminishing returns on traditional social media advertising channels.",
                    "Data from quick-commerce platforms shows a 60% increase in one-off premium coffee orders, suggesting a shift away from fixed recurring monthly subscription models entirely.",
                    "Transaction records reveal that 55% of users who cancel their subscription cite budget reallocation toward experiential spending like travel and dining as their primary reason.",
                    "Inventory levels for specialized subscription-only coffee roasters have reported a 20% surplus, forcing many to pivot toward wholesale or supermarket retail distribution strategies recently."
                ],
                "peripheral_layer": [
                    "The rise of high-interest rates has led to a broader contraction in discretionary spending across all premium digital services, not just the niche coffee market segment.",
                    "Adjacent industries such as meal kit delivery services are reporting similar abandonment patterns, indicating a systemic shift in how Gen-Z manages recurring personal expenses.",
                    "The rapid growth of the second-hand market and thrift economy shows a growing preference for sustainability and value over high-status new subscription consumption habits today.",
                    "Social media platforms are pivoting toward 'de-influencing' content, which encourages consumers to stop buying unnecessary premium products and cancel their recurring expensive digital subscriptions.",
                    "Global logistics costs have increased by 15% on average, forcing brands to pass those costs onto consumers through higher monthly fees which further accelerates churn rates.",
                    "Work-from-home policy reversals in major corporate sectors are reducing the need for premium home coffee setups as employees return to office-provided beverage solutions twice weekly.",
                    "The emergence of low-cost, high-quality private label options from large supermarkets is cannibalizing the bottom end of the artisan subscription market significantly among price-conscious youth."
                ]
            }
        else:
            data = extract_json(raw_response)

        if data:
            validation = validate_pipeline_data(data, schema)
            if validation["valid"]:
                if len(data["direct_layer"]) == 7 and len(data["peripheral_layer"]) == 7:
                    data["step3_lineage"] = step3_data
                    return data
                else:
                    logger.warning("Did not get exactly 7 items in layers. Retrying...")

        attempts += 1
    return None

if __name__ == "__main__":
    try:
        if not sys.stdin.isatty():
            input_data = json.load(sys.stdin)
        else:
            input_data = json.loads(sys.argv[1])
        
        result = extract_outcomes(input_data)
        if result:
            print(json.dumps(result, indent=2))
        else:
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error in Step 4: {str(e)}")
        sys.exit(1)
