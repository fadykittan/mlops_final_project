#!/usr/bin/env python3
"""
Test script for the DAG Validator.
Demonstrates how to use the DAGValidator class to validate generated Airflow DAGs.

** This app file is for testing only **
"""

from dag_validator import DAGValidator
import json


def main():
    """Test the DAG validator with the generated pipeline file."""
    
    # Initialize validator
    validator = DAGValidator()
    
    # Test with the generated DAG file
    dag_filename = "file_to_file_etl_pipeline_final.py"
    
    print(f"Validating DAG file: {dag_filename}")
    print("=" * 50)
    
    # Perform validation
    result = validator.validate_dag(dag_filename)
    
    # Display results
    print(f"File: {result['file_path']}")
    print(f"Success: {result['success']}")
    print()
    
    if result['errors']:
        print("ERRORS:")
        for error in result['errors']:
            print(f"  ❌ {error}")
        print()
    
    if result['warnings']:
        print("WARNINGS:")
        for warning in result['warnings']:
            print(f"  ⚠️  {warning}")
        print()
    
    if result['success'] and not result['warnings']:
        print("✅ DAG validation passed with no issues!")
    elif result['success']:
        print("✅ DAG validation passed with warnings.")
    else:
        print("❌ DAG validation failed.")
    
    # Pretty print full result as JSON
    print("\nFull validation result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
