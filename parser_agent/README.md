# Parser Agent Flask App

A simple Flask application that provides an endpoint to receive and process requests.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

The app will start on `http://localhost:5000`

## Endpoints

### POST /parse
Receives a JSON body with the following format:
```json
{
  "req": "abc"
}
```

**Response:**
```json
{
  "status": "success",
  "received_request": "abc",
  "message": "Successfully received request: abc"
}
```

### GET /health
Health check endpoint that returns the status of the service.

**Response:**
```json
{
  "status": "healthy",
  "message": "Parser agent is running"
}
```

## Example Usage

```bash
# Test the parse endpoint
curl -X POST http://localhost:5000/parse \
  -H "Content-Type: application/json" \
  -d '{"req": "abc"}'

# Test the health endpoint
curl http://localhost:5000/health
```
