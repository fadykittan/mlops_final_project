import ast
import os
from typing import Dict, List, Tuple


class DAGValidator:
    """
    A simple validator class for Airflow DAG files.
    Performs both Python syntax validation and Airflow-specific validation.
    """
    
    def __init__(self):
        self.pipeline_output_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'pipeline_generator_agent', 
            'output'
        )
    
    def validate_dag(self, filename: str) -> Dict:
        """
        Validate an Airflow DAG file.
        
        Args:
            filename (str): Name of the DAG file to validate
            
        Returns:
            Dict: Validation results with success, errors, warnings, and file_path
        """
        file_path = os.path.join(self.pipeline_output_dir, filename)
        
        # Initialize result structure
        result = {
            'success': True,
            'errors': [],
            'warnings': [],
            'file_path': file_path
        }
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                result['success'] = False
                result['errors'].append(f"File not found: {file_path}")
                return result
            
            # Read file content
            with open(file_path, 'r') as f:
                code = f.read()
            
            # Perform Python syntax validation
            syntax_valid, syntax_errors = self._check_syntax(code)
            if not syntax_valid:
                result['success'] = False
                result['errors'].extend(syntax_errors)
            
            # Perform Airflow-specific validation
            airflow_errors, airflow_warnings = self._check_airflow_structure(code)
            if airflow_errors:
                result['success'] = False
                result['errors'].extend(airflow_errors)
            
            result['warnings'].extend(airflow_warnings)
            
        except Exception as e:
            result['success'] = False
            result['errors'].append(f"Unexpected error during validation: {str(e)}")
        
        return result
    
    def _check_syntax(self, code: str) -> Tuple[bool, List[str]]:
        """
        Check Python syntax using ast.parse().
        
        Args:
            code (str): Python code to validate
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        try:
            ast.parse(code)
            return True, errors
        except SyntaxError as e:
            errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
            return False, errors
        except Exception as e:
            errors.append(f"Parse error: {str(e)}")
            return False, errors
    
    def _check_airflow_structure(self, code: str) -> Tuple[List[str], List[str]]:
        """
        Check Airflow-specific structure and requirements.
        
        Args:
            code (str): Python code to validate
            
        Returns:
            Tuple[List[str], List[str]]: (errors, warnings)
        """
        errors = []
        warnings = []
        
        try:
            tree = ast.parse(code)
        except:
            # If we can't parse the code, skip Airflow validation
            return errors, warnings
        
        # Check for required Airflow imports
        has_airflow_import = False
        has_dag_import = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == 'airflow':
                    has_airflow_import = True
                    for alias in node.names:
                        if alias.name == 'DAG':
                            has_dag_import = True
                            break
        
        if not has_airflow_import:
            errors.append("Missing required import: 'from airflow import DAG'")
        elif not has_dag_import:
            errors.append("Missing DAG import from airflow module")
        
        # Check for DAG object creation
        has_dag_creation = False
        dag_id = None
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if (isinstance(node.func, ast.Name) and node.func.id == 'DAG') or \
                   (isinstance(node.func, ast.Attribute) and node.func.attr == 'DAG'):
                    has_dag_creation = True
                    
                    # Try to extract dag_id
                    for keyword in node.keywords:
                        if keyword.arg == 'dag_id' and isinstance(keyword.value, ast.Constant):
                            dag_id = keyword.value.value
                            break
                    break
        
        if not has_dag_creation:
            errors.append("No DAG object creation found")
        
        # Check for task definitions
        task_count = 0
        task_operators = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for common Airflow operators
                if isinstance(node.func, ast.Attribute):
                    # Check for operators ending with 'Operator' or 'Sensor', or specific operators
                    if (node.func.attr.endswith('Operator') or 
                        node.func.attr.endswith('Sensor') or 
                        node.func.attr == 'PythonVirtualenvOperator'):
                        task_count += 1
                        task_operators.append(node.func.attr)
                elif isinstance(node.func, ast.Name):
                    # Check for direct operator names
                    if (node.func.id.endswith('Operator') or 
                        node.func.id.endswith('Sensor') or 
                        node.func.id == 'PythonVirtualenvOperator'):
                        task_count += 1
                        task_operators.append(node.func.id)
        
        if task_count == 0:
            errors.append("No Airflow tasks found in DAG")
        elif task_count == 1:
            warnings.append("Only one task found - consider if this is intentional")
        
        # Check for task dependencies (>> operator usage)
        has_dependencies = False
        for node in ast.walk(tree):
            if isinstance(node, ast.RShift):  # >> operator
                has_dependencies = True
                break
        
        if task_count > 1 and not has_dependencies:
            warnings.append("Multiple tasks found but no task dependencies (>>) detected")
        
        # Additional checks
        if dag_id and len(dag_id) > 250:
            warnings.append(f"DAG ID '{dag_id}' is longer than 250 characters")
        
        return errors, warnings
