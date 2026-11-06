from airflow.models import DagBag
import pytest


def test_no_import_errors():
    """Test che verifica che non ci siano errori di importazione o sintassi nei DAG."""
    dag_bag = DagBag(dag_folder="airflow-project/dags", include_examples=False)
    assert len(dag_bag.import_errors) == 0, f"Errori di importazione nei DAG: {dag_bag.import_errors}"


def test_dag_loaded():
    """Test che verifica che siano stati caricati correttamente dei DAG."""
    dag_bag = DagBag(dag_folder="airflow-project/dags", include_examples=False)
    assert len(dag_bag.dags) > 0, "Nessun DAG trovato nella cartella dags!"