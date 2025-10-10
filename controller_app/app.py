from flask import Flask, request, jsonify
from controller import run_flow

app = Flask(__name__)

@app.route('/flow', methods=['POST'])
def flow_endpoint():
    try:
        data = request.get_json()
        
        if not data or 'req' not in data:
            return jsonify({'error': 'Missing required field: req'}), 400
        
        req_value = data['req']
        result = run_flow(req_value)
        
        return jsonify(result), 200 if result["status"] == "success" else 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8002)
