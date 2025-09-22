from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/parse', methods=['POST'])
def parse_request():
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
        
        # Process the request (you can add your parsing logic here)
        response_data = {
            'status': 'success',
            'received_request': req_value,
            'message': f'Successfully received request: {req_value}'
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
