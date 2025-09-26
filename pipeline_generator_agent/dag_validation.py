import pathlib
from airflow.models import DagBag

def test_no_import_errors():
    dags_path = pathlib.Path("../airflow/dags")  # or the folder/file you want
    bag = DagBag(dag_folder=str(dags_path), include_examples=False)
    assert not bag.import_errors, f"Import errors: {bag.import_errors}"

def test_all_dags_load_and_have_tasks():
    bag = DagBag(dag_folder="../airflow/dags", include_examples=False)
    for dag_id, dag in bag.dags.items():
        assert dag.tasks, f"{dag_id} has no tasks"

if __name__ == "__main__":
    test_no_import_errors()
    test_all_dags_load_and_have_tasks()
