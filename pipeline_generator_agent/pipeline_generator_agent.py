from datetime import datetime
import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables from config.env file
load_dotenv(os.path.join(os.path.dirname(__file__), 'config.env'))

def save_dag_to_file(dag_code: str, filename: str = None) -> str:
    """
    Save the generated DAG code to a Python file.
    
    Args:
        dag_code (str): The generated DAG code
        filename (str): Optional filename. If not provided, generates from DAG ID
    
    Returns:
        str: The file path where the DAG was saved
    """
    if not filename:
        # Extract DAG ID from the code
        import re
        dag_id_match = re.search(r"dag_id\s*=\s*['\"]([^'\"]+)['\"]", dag_code)
        if dag_id_match:
            dag_id = dag_id_match.group(1)
            filename = f"{dag_id}.py"
        else:
            filename = "generated_dag.py"
    
    # Ensure the filename has .py extension
    if not filename.endswith('.py'):
        filename += '.py'
    
    # Save to output directory
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = os.path.join(output_dir, filename)
    
    with open(file_path, 'w') as f:
        f.write(dag_code)
    
    print(f"DAG saved to: {file_path}")
    return file_path

def generate_pipeline(pipeline_spec: dict, save_to_file: bool = True) -> str:
    """
    Generate an Airflow DAG from a pipeline specification JSON.
    
    Args:
        pipeline_spec (dict): The pipeline specification JSON
        save_to_file (bool): Whether to save the generated DAG to a file
    
    Returns:
        str: Complete Airflow DAG Python code ready to run
    """
    try:
        # Initialize Google Gemini model
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.1,
            convert_system_message_to_human=True,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        # Read system prompt from file
        system_prompt_path = os.path.join(os.path.dirname(__file__), 'system_prompt.txt')
        with open(system_prompt_path, 'r') as f:
            system_prompt = f.read()

        # Create a simple prompt using the system prompt from file
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Generate an Airflow DAG from this pipeline specification: {pipeline_spec}")
        ])
        
        # Create the chain: prompt | model
        chain = prompt | model
        
        # Execute the generation
        result = chain.invoke({"pipeline_spec": json.dumps(pipeline_spec)})
        
        # Extract the content from the response
        dag_code = result.content
        
        # Clean up any markdown formatting
        if dag_code.startswith('```python'):
            dag_code = dag_code.replace('```python', '').replace('```', '').strip()
        elif dag_code.startswith('```'):
            dag_code = dag_code.replace('```', '').strip()
        
        print("--------------------------------")
        print("Generated Airflow DAG:")
        print(dag_code)
        print("--------------------------------")
        
        # Save to file if requested
        if save_to_file:
            save_dag_to_file(dag_code)
        
        return dag_code
        
    except Exception as e:
        error_msg = f"Error generating pipeline: {str(e)}"
        print(f"Error: {error_msg}")
        return f"# Error generating pipeline: {error_msg}\n# Original spec: {json.dumps(pipeline_spec, indent=2)}"


if __name__ == "__main__":
    # Demo pipeline specification for testing
    sample_pipeline_spec = {
        "user_request": "Create an ETL pipeline to pull daily sales data from the Shopify API, the endpoint is google.com/api/v1/sales, clean null customer IDs, and load it into Postgres with a daily_sales table.",
        "source": {
            "type": "API",
            "endpoint_or_table": "google.com/api/v1/sales",
            "query_or_filter": None
        },
        "destination": {
            "type": "Postgres",
            "path": "daily_sales"
        },
        "transformations": [
            {
                "step_number": 1,
                "language": "Python",
                "operation": "Null Customer ID Handling",
                "target": "customer_id"
            }
        ],
        "confidence": 0.8
    }

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
    
    # Create generator instance and generate the pipeline
    result = generate_pipeline(sample_pipeline_spec)
    
    # Pretty print the results
    print(result)
