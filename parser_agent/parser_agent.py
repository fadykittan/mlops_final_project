from datetime import datetime
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

# Load environment variables from config.env file
load_dotenv(os.path.join(os.path.dirname(__file__), 'config.env'))

# Define response schemas for structured output matching the system prompt
response_schemas = [
    ResponseSchema(name="user_request", description="The original user request"),
    ResponseSchema(name="source", description="Source configuration with type, endpoint_or_table, and query_or_filter"),
    ResponseSchema(name="destination", description="Destination configuration with type and path"),
    ResponseSchema(name="transformations", description="List of transformation steps with step_number, language, operation, and target"),
    ResponseSchema(name="confidence", description="Overall parse confidence score from 0-1")
]

# Create the output parser
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

def parse_request(request: str) -> dict:
    """
    Parse a request using Google Gemini AI to extract detailed requirements.
    
    Args:
        request (str): The input request to parse
    
    Returns:
        dict: Structured output with parsed requirements
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
        system_prompt_path = os.path.join(os.path.dirname(__file__), 'sysyem_prompt.txt')
        with open(system_prompt_path, 'r') as f:
            system_prompt = f.read()

        # Create custom format instructions to avoid template variable conflicts
        format_instructions = """The output should be a valid JSON object with the following structure:
{{
    "user_request": "string - The original user request",
    "source": "object - Source configuration with type, endpoint_or_table, and query_or_filter",
    "destination": "object - Destination configuration with type and path", 
    "transformations": "array - List of transformation steps with step_number, language, operation, and target",
    "confidence": "number - Overall parse confidence score from 0-1"
}}

Return ONLY the JSON object, no additional text or markdown formatting."""

        # Create a simple prompt without template variables in system message
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are the Request Parser Agent for FlowForge's DataOps Assistant. Your job is to convert a natural-language request into a structured ETL pipeline specification in strict JSON.\n\n{format_instructions}"),
            ("human", "Parse this request into detailed requirements: {request}")
        ])
        
        # Create the chain: prompt | model | parser
        chain = prompt | model | output_parser
        
        # Execute the parsing
        result = chain.invoke({"request": request})
        
        print("--------------------------------")
        print("Parsed Requirements:")
        print(result)
        print("--------------------------------")
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "original_request": request,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Demo request for testing
    sample_request = """
    Create an ETL pipeline to pull daily sales data from the Shopify API, the endpoint is google.com/api/v1/sales, clean null customer IDs, and load it into Postgres with a daily_sales table.
    """
    
    # Create parser instance and parse the request
    result = parse_request(sample_request)
    
    # Pretty print the results
    print(result)

