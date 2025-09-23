from flask import Flask, request, jsonify
from pipeline_generator_agent import generate_pipeline
import json

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate_pipeline_endpoint():
    """
    Generate an Airflow DAG from a pipeline specification.
    
    Expected JSON payload:
    {
        "pipeline_spec": {
            "user_request": "string",
            "source": {...},
            "destination": {...},
            "transformations": [...],
            "confidence": 0.8
        }
    }
    
    Returns:
    - Content-Type: text/plain (Python code)
    - 200: Generated DAG code
    - 400: Bad request
    - 500: Server error
    """
    try:
        data = request.get_json()
        
        if not data or 'pipeline_spec' not in data:
            return jsonify({
                "error": "Missing 'pipeline_spec' in request body",
                "status": "error"
            }), 400
        
        pipeline_spec = data['pipeline_spec']
        
        # Generate the pipeline
        dag_code = generate_pipeline(pipeline_spec)
        
        # Return the Python code as plain text
        return dag_code, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "pipeline_generator_agent"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
