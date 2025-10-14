import shutil
from pathlib import Path

class DeploymentAgent:
    """Simple deployment agent that copies or moves files."""
    
    def __init__(self, source_dir=None, target_dir=None):
        # Set paths - use provided paths or defaults
        if source_dir and target_dir:
            self.source_dir = Path(source_dir)
            self.target_dir = Path(target_dir)
        else:
            # Default paths relative to project root
            project_root = Path(__file__).parent.parent
            self.source_dir = project_root / "pipeline_generator_agent" / "output"
            self.target_dir = project_root / "airflow" / "dags"
        
        # Ensure target directory exists
        self.target_dir.mkdir(parents=True, exist_ok=True)
    
    def deploy_file(self, filename, operation="copy"):
        """Deploy a specific file using copy or move operation."""
        source_file = self.source_dir / filename
        target_file = self.target_dir / filename
        
        if not source_file.exists():
            print(f"Source file not found: {source_file}")
            return False
        
        try:
            if operation == "move":
                shutil.move(str(source_file), str(target_file))
                print(f"Moved: {filename}")
            else:  # default to copy
                shutil.copy2(source_file, target_file)
                print(f"Copied: {filename}")
            return True
        except Exception as e:
            print(f"Error {operation}ing {filename}: {e}")
            return False
    
    def deploy_all_dags(self, operation="copy"):
        """Deploy all .py files from source to target directory."""
        if not self.source_dir.exists():
            print(f"Source directory not found: {self.source_dir}")
            return []
        
        deployed_files = []
        for file_path in self.source_dir.glob("*.py"):
            if self.deploy_file(file_path.name, operation):
                deployed_files.append(file_path.name)
        
        print(f"Deployed {len(deployed_files)} DAG files using {operation}")
        return deployed_files
    
    def get_deployed_path(self, filename):
        """Get the full path where a file would be deployed."""
        return str(self.target_dir / filename)


if __name__ == "__main__":
    # Demo usage with different options
    
    # Example 1: Default paths, copy all files
    print("=== Example 1: Default paths, copy all ===")
    agent1 = DeploymentAgent()
    agent1.deploy_all_dags()
    
    # Example 2: Custom paths, copy specific file
    print("\n=== Example 2: Custom paths, copy specific file ===")
    agent2 = DeploymentAgent(
        source_dir="/Users/fadykittan/dev/mlops_final_project/pipeline_generator_agent/output",
        target_dir="/Users/fadykittan/dev/mlops_final_project/airflow/dags"
    )
    agent2.deploy_file("file_to_file_etl_pipeline_final.py", "copy")
    
    # Example 3: Move operation
    print("\n=== Example 3: Move operation ===")
    agent3 = DeploymentAgent()
    agent3.deploy_file("file_to_file_etl_pipeline_final.py", "move")
