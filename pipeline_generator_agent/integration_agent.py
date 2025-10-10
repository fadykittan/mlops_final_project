import os
from pipeline_generator_agent.pipeline_generator_agent import generate_pipeline
from pipeline_generator_agent.judge_agent import JudgeAgent

class IntegrationAgent:
    def __init__(self):
        """Initialize the integration agent with generator and judge."""
        self.generator = None  # Will use the generate_pipeline function directly
        self.judge = JudgeAgent()
        self.max_retries = 3

    def generate_and_validate_pipeline(self, pipeline_spec: dict) -> dict:
        """
        Generate a pipeline and validate it with the judge.
        
        Args:
            pipeline_spec (dict): The pipeline specification
            
        Returns:
            dict: Result with success status, DAG code, and evaluation
        """
        print(f"Starting pipeline generation with max {self.max_retries} retries...")
        
        for attempt in range(1, self.max_retries + 1):
            print(f"\n--- Attempt {attempt}/{self.max_retries} ---")
            
            try:
                # Generate the pipeline
                print("Generating pipeline...")
                dag_code = generate_pipeline(pipeline_spec, save_to_file=False)
                
                # Judge the generated pipeline
                print("Evaluating pipeline quality...")
                evaluation = self.judge.evaluate_dag(dag_code)
                
                print(f"Judge Score: {evaluation['score']}/100")
                print(f"Passed: {evaluation['passed']}")
                
                if evaluation['issues']:
                    print(f"Issues found: {evaluation['issues']}")
                
                if evaluation['passed']:
                    print("✅ Pipeline generation successful!")
                    return {
                        "success": True,
                        "attempt": attempt,
                        "dag_code": dag_code,
                        "evaluation": evaluation,
                        "message": "Pipeline generated and validated successfully"
                    }
                else:
                    print(f"❌ Pipeline failed validation (Score: {evaluation['score']})")
                    if attempt < self.max_retries:
                        print("Retrying with feedback...")
                        # Add feedback to pipeline spec for next attempt
                        pipeline_spec = self._add_feedback_to_spec(pipeline_spec, evaluation)
                    else:
                        print("Max retries reached. Returning best attempt.")
                        return {
                            "success": False,
                            "attempt": attempt,
                            "dag_code": dag_code,
                            "evaluation": evaluation,
                            "message": f"Pipeline failed validation after {self.max_retries} attempts"
                        }
                        
            except Exception as e:
                print(f"❌ Error in attempt {attempt}: {str(e)}")
                if attempt == self.max_retries:
                    return {
                        "success": False,
                        "attempt": attempt,
                        "error": str(e),
                        "message": f"Pipeline generation failed after {self.max_retries} attempts"
                    }
                print("Retrying...")
        
        # This should never be reached, but just in case
        return {
            "success": False,
            "attempt": self.max_retries,
            "message": "Unexpected error in pipeline generation"
        }

    def _add_feedback_to_spec(self, pipeline_spec: dict, evaluation: dict) -> dict:
        """
        Add judge feedback to the pipeline specification for retry.
        
        Args:
            pipeline_spec (dict): Original pipeline specification
            evaluation (dict): Judge evaluation results
            
        Returns:
            dict: Updated pipeline specification with feedback
        """
        # Create a copy to avoid modifying the original
        updated_spec = pipeline_spec.copy()
        
        # Add feedback as additional context
        feedback = {
            "previous_issues": evaluation.get("issues", []),
            "suggestions": evaluation.get("suggestions", []),
            "score": evaluation.get("score", 0)
        }
        
        # Add feedback to the user request
        if "feedback" not in updated_spec:
            updated_spec["feedback"] = []
        updated_spec["feedback"].append(feedback)
        
        return updated_spec

    def save_final_dag(self, dag_code: str, filename: str = None) -> str:
        """
        Save the final DAG code to a file.
        
        Args:
            dag_code (str): The DAG code to save
            filename (str): Optional filename
            
        Returns:
            str: Path to the saved file
        """
        if not filename:
            # Extract DAG ID from the code
            import re
            dag_id_match = re.search(r"dag_id\s*=\s*['\"]([^'\"]+)['\"]", dag_code)
            if dag_id_match:
                dag_id = dag_id_match.group(1)
                filename = f"{dag_id}_final.py"
            else:
                filename = "generated_dag_final.py"
        
        # Ensure the filename has .py extension
        if not filename.endswith('.py'):
            filename += '.py'
        
        # Save to output directory
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        file_path = os.path.join(output_dir, filename)
        
        with open(file_path, 'w') as f:
            f.write(dag_code)
        
        print(f"Final DAG saved to: {file_path}")
        return file_path


if __name__ == "__main__":
    # Test the integration agent
    integration = IntegrationAgent()
    
    # Sample pipeline specification
    sample_pipeline_spec = {
        "user_request": "Create an ETL pipeline to read data from local file called in.txt, and load it another file called out.txt",
        "source": {
            "type": "file",
            "endpoint_or_table": "in.txt",
            "query_or_filter": "null"
        },
        "destination": {
            "type": "file",
            "path": "out.txt"
        },
        "transformations": [],
        "confidence": 0.95
    }
    
    print("Testing Integration Agent...")
    result = integration.generate_and_validate_pipeline(sample_pipeline_spec)
    
    print("\n" + "="*50)
    print("FINAL RESULT:")
    print("="*50)
    print(f"Success: {result['success']}")
    print(f"Attempts: {result['attempt']}")
    print(f"Message: {result['message']}")
    
    if result['success']:
        print("\nSaving final DAG...")
        integration.save_final_dag(result['dag_code'])
        print("\nGenerated DAG Code:")
        print("-" * 30)
        print(result['dag_code'])
    else:
        print(f"\nFailed to generate acceptable pipeline after {result['attempt']} attempts.")
        if 'evaluation' in result:
            print(f"Final score: {result['evaluation']['score']}")
            print(f"Issues: {result['evaluation']['issues']}")
