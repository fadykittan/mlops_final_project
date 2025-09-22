from datetime import datetime
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables from config.env file
load_dotenv(os.path.join(os.path.dirname(__file__), 'config.env'))

def parse_request(request: str) -> str:
    """
    Parse a request using Google Gemini AI to extract detailed requirements.
    
    Args:
        request (str): The input request to parse
    
    Returns:
        str
    """
    try:
        # Initialize Google Gemini model
        # Note: Set GOOGLE_API_KEY environment variable
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

        # Escape curly braces in the system prompt to prevent template variable interpretation
        system_prompt_escaped = system_prompt.replace('{', '{{').replace('}', '}}')

        # Create prompt template - placeholder for custom prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt_escaped),
            ("human", "Parse this request into detailed requirements: {request}")
        ])
        
        # Execute the parsing directly with the LLM
        result = model.invoke(
            prompt.format_messages(request=request)
        )
        
        print("--------------------------------")
        # return {
        #     "status": "success",
        #     "original_request": request,
        #     "parsed_requirements": result.content,
        #     "timestamp": datetime.now().isoformat(),
        #     "model_used": "gemini-1.5-flash"
        # }
        print(result.content)
        return result.content
        
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
    Create an ETL pipeline to pull daily sales data from the Shopify API, clean null customer IDs, and load it into Postgres with a daily_sales table.
    """
    
    # Create parser instance and parse the request
    result = parse_request(sample_request)
    
    # Pretty print the results
    print(result)

