import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser_agent.parser_agent import parse_request
from pipeline_generator_agent.integration_agent import IntegrationAgent
from validation_agent.dag_validator import DAGValidator

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
        
        # 4. Check if pipeline generation was successful
        if not result["success"]:
            return {"status": "failed", "error": result.get("message", "Pipeline generation failed")}
        
        # 5. Save the generated DAG to file first (for validation)
        try:
            saved_file_path = integration.save_final_dag(result["dag_code"])
        except Exception as save_error:
            return {"status": "failed", "error": f"Pipeline generated but failed to save: {str(save_error)}"}
        
        # 6. Validate the generated DAG using the validation agent
        validator = DAGValidator()
        dag_filename = os.path.basename(saved_file_path)
        validation_result = validator.validate_dag(dag_filename)
        
        # 7. Check validation results
        if not validation_result["success"]:
            return {
                "status": "failed", 
                "error": f"DAG validation failed: {'; '.join(validation_result['errors'])}",
                "validation_details": validation_result
            }
        
        # 8. Return success with validation info
        response = {
            "status": "success", 
            "saved_file": saved_file_path,
            "validation": {
                "success": validation_result["success"],
                "warnings": validation_result.get("warnings", [])
            }
        }
        
        return response
    
    except Exception as e:
        return {"status": "failed", "error": str(e)}
