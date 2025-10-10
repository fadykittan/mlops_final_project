import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser_agent.parser_agent import parse_request
from pipeline_generator_agent.integration_agent import IntegrationAgent

def run_flow(req):
    """
    Run the MLOps pipeline flow
    """
    try:
        # 1. Parse the request
        parsed_result = parse_request(req)
        
        # 2. Check if parsing had errors
        if "error" in parsed_result:
            return {"status": "failed", "error": parsed_result["error"]}
        
        # 3. Generate and validate pipeline
        integration = IntegrationAgent()
        result = integration.generate_and_validate_pipeline(parsed_result)
        
        # 4. Return success/failure based on result
        if result["success"]:
            return {"status": "success"}
        else:
            return {"status": "failed", "error": result.get("message", "Pipeline generation failed")}
    
    except Exception as e:
        return {"status": "failed", "error": str(e)}
