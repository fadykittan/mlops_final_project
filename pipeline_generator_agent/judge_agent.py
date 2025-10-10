import os
import ast
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'config.env'))

class JudgeAgent:
    def __init__(self):
        """Initialize the judge agent with Google Gemini model."""
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,
            convert_system_message_to_human=True,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        self.judge_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a code quality judge for Airflow DAGs. Evaluate the generated DAG code and provide a score from 0-100.

Evaluation Criteria:
1. **Syntax & Structure (25 points)**: Valid Python syntax, proper Airflow DAG structure
2. **Functionality (25 points)**: Implements the required ETL operations correctly
3. **Best Practices (25 points)**: Follows Airflow conventions, proper task dependencies
4. **Error Handling (25 points)**: Includes appropriate error handling and logging

Return ONLY a JSON response with this exact format:
{{
    "score": <number>,
    "passed": <true/false>,
    "issues": ["list of specific issues found"],
    "suggestions": ["list of improvement suggestions"]
}}

A score of 70+ is considered passing."""),
            ("human", "Evaluate this Airflow DAG code:\n\n{dag_code}")
        ])

    def evaluate_dag(self, dag_code: str) -> dict:
        """
        Evaluate the quality of a generated DAG.
        
        Args:
            dag_code (str): The DAG code to evaluate
            
        Returns:
            dict: Evaluation results with score, passed status, and feedback
        """
        try:
            # Basic syntax check first
            syntax_valid = self._check_syntax(dag_code)
            if not syntax_valid:
                return {
                    "score": 0,
                    "passed": False,
                    "issues": ["Invalid Python syntax"],
                    "suggestions": ["Fix syntax errors before evaluation"]
                }
            
            # Use AI model for detailed evaluation
            chain = self.judge_prompt | self.model
            result = chain.invoke({"dag_code": dag_code})
            
            # Parse the JSON response
            response_text = result.content.strip()
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            try:
                evaluation = json.loads(response_text)
                return evaluation
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "score": 50,
                    "passed": False,
                    "issues": ["Could not parse evaluation response"],
                    "suggestions": ["Retry evaluation"]
                }
                
        except Exception as e:
            return {
                "score": 0,
                "passed": False,
                "issues": [f"Evaluation error: {str(e)}"],
                "suggestions": ["Check the DAG code for obvious issues"]
            }

    def _check_syntax(self, code: str) -> bool:
        """Check if the code has valid Python syntax."""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def is_acceptable(self, dag_code: str) -> bool:
        """
        Simple check if the DAG is acceptable (score >= 70).
        
        Args:
            dag_code (str): The DAG code to check
            
        Returns:
            bool: True if acceptable, False otherwise
        """
        evaluation = self.evaluate_dag(dag_code)
        return evaluation.get("passed", False) and evaluation.get("score", 0) >= 70


if __name__ == "__main__":
    # Test the judge agent
    judge = JudgeAgent()
    
    # Test with a simple DAG
    test_dag = """
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

def hello_world():
    print("Hello World!")

dag = DAG(
    'test_dag',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily'
)

task = PythonOperator(
    task_id='hello_task',
    python_callable=hello_world,
    dag=dag
)
"""
    
    result = judge.evaluate_dag(test_dag)
    print("Judge evaluation result:")
    print(f"Score: {result['score']}")
    print(f"Passed: {result['passed']}")
    print(f"Issues: {result['issues']}")
    print(f"Suggestions: {result['suggestions']}")
