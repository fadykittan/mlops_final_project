from flask import Flask, request, jsonify
from parser_agent import parse_request

app = Flask(__name__)

@app.route('/parse', methods=['POST'])
def parse_endpoint():
    """
    Endpoint that receives a JSON body with 'req' field
    """
    try:
        # Get JSON data from request body
        data = request.get_json()
        
        # Check if 'req' field exists in the request
        if not data or 'req' not in data:
            return jsonify({
                'error': 'Missing required field: req',
                'status': 'error'
            }), 400
        
        # Extract the 'req' value
        req_value = data['req']
        
        # Process the request using the parser agent
        parsed_result = parse_request(req_value)
        
        # Return the parsed result from the parser agent
        response_data = {
            'status': 'success',
            'original_request': req_value,
            'parsed_result': parsed_result
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        'status': 'healthy',
        'message': 'Parser agent is running'
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)
