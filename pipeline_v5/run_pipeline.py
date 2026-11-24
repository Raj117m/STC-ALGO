"""
STC ALGO V5 - Master Orchestrator (run_pipeline.py)
"""

import os
import json
import time
import threading
from typing import Dict, Any

from utils import save_state, load_state, STATE_FILE

# Import step modules
import step1_intent_processing
import step2_intent_cluster
import step3_conscious_expressions
import step4_tangible_footprints
import step5_tension_detection
import step6_pattern_compression
import step7_refinement_loop
import step8_final_output

def run_v5_pipeline(query: str):
    """Executes all 8 steps of the V5 pipeline."""
    try:
        # Initial status
        print("STATUS: PIPELINE_START")
        
        # Step 1: Intent Processing
        print("STATUS: STEP_1_START")
        s1_data = step1_intent_processing.process_intent(query)
        if not s1_data: raise Exception("Step 1 failed")
        save_state(1, s1_data, "INTENT_PROCESSED")
        
        # Step 2: Context Refiner
        print("STATUS: STEP_2_START")
        s2_data = step2_intent_cluster.refine_intent(s1_data)
        if not s2_data: raise Exception("Step 2 failed")
        save_state(2, s2_data, "CLUSTER_REFINED")
        
        # Step 3: Ideology Extraction
        print("STATUS: STEP_3_START")
        s3_data = step3_conscious_expressions.extract_ideology(s2_data)
        if not s3_data: raise Exception("Step 3 failed")
        save_state(3, s3_data, "IDEOLOGY_EXTRACTED")
        
        # Step 4: Outcome Extraction
        print("STATUS: STEP_4_START")
        s4_data = step4_tangible_footprints.extract_outcomes(s3_data)
        if not s4_data: raise Exception("Step 4 failed")
        save_state(4, s4_data, "OUTCOMES_EXTRACTED")
        
        # Step 5: Contradiction Finder
        print("STATUS: STEP_5_START")
        s5_data = step5_tension_detection.detect_tension(s4_data)
        if not s5_data: raise Exception("Step 5 failed")
        save_state(5, s5_data, "TENSION_DETECTED")
        
        # Step 6: Signature Generation
        print("STATUS: STEP_6_START")
        s6_data = step6_pattern_compression.compress_patterns(s5_data)
        if not s6_data: raise Exception("Step 6 failed")
        save_state(6, s6_data, "SIGNATURES_GENERATED")
        
        # Step 7: Refinement Loop
        print("STATUS: STEP_7_START")
        s7_data = step7_refinement_loop.evolve_cluster(s6_data)
        if not s7_data: raise Exception("Step 7 failed")
        save_state(7, s7_data, "CLUSTER_EVOLVED")
        
        # Step 8: Executive Briefing
        print("STATUS: STEP_8_START")
        s8_data = step8_final_output.generate_report(s7_data)
        if not s8_data: raise Exception("Step 8 failed")
        save_state(8, s8_data, "REPORT_GENERATED")
        
        print("STATUS: PIPELINE_COMPLETE")
        return s8_data
        
    except Exception as e:
        print(f"STATUS: ERROR - {str(e)}")
        # Partial data is already saved in STATE_FILE
        return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = sys.argv[1]
        run_v5_pipeline(query)
    else:
        print("Usage: python3 run_pipeline.py '<query>'")
