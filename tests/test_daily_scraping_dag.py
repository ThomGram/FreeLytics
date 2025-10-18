import os
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


class TestDailyScrapingDag:
    """Tests for the orchestrator DAG that triggers scraping and dbt pipelines"""

    def setup_method(self):
        # Mock Airflow environment
        os.environ["AIRFLOW__CORE__EXECUTOR"] = "SequentialExecutor"
        os.environ["AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"] = "sqlite:///test_airflow.db"

        # Mock airflow modules
        mock_airflow = MagicMock()
        mock_python_operator = MagicMock()
        mock_trigger_dagrun = MagicMock()

        sys.modules["airflow"] = mock_airflow
        sys.modules["airflow.models"] = mock_airflow.models
        sys.modules["airflow.operators"] = mock_airflow.operators
        sys.modules["airflow.operators.python"] = mock_python_operator
        sys.modules["airflow.operators.trigger_dagrun"] = mock_trigger_dagrun

        # Import the DAG module after mocking
        sys.path.insert(0, "airflow/dags")
        self.dag_module = __import__("daily_scraping_pipeline")

    def test_dag_loaded(self):
        """Test that the orchestrator DAG is loaded correctly"""
        assert self.dag_module.dag is not None
        assert hasattr(self.dag_module, "dag")

    def test_dag_structure(self):
        """Test DAG has correct orchestrator structure"""
        # Orchestrator DAG triggers other DAGs
        assert hasattr(self.dag_module, "trigger_scraping")
        assert hasattr(self.dag_module, "trigger_dbt")

    def test_dag_default_args(self):
        """Test DAG has correct default arguments"""
        default_args = self.dag_module.default_args

        assert default_args["owner"] == "freelytics"
        assert default_args["depends_on_past"] is False

    def test_no_import_errors(self):
        """Test that the orchestrator DAG module can be imported without errors"""
        assert self.dag_module is not None
        # Orchestrator has trigger operators, not direct task functions
        assert hasattr(self.dag_module, "dag")


class TestScrapingPipeline:
    """Tests for the scraping pipeline DAG"""

    def setup_method(self):
        # Mock Airflow modules
        mock_airflow = MagicMock()
        mock_python_operator = MagicMock()

        sys.modules["airflow"] = mock_airflow
        sys.modules["airflow.models"] = mock_airflow.models
        sys.modules["airflow.operators"] = mock_airflow.operators
        sys.modules["airflow.operators.python"] = mock_python_operator

        sys.path.insert(0, "airflow/dags")
        self.dag_module = __import__("scraping_pipeline")

    def test_scraping_dag_loaded(self):
        """Test that scraping DAG is loaded"""
        assert self.dag_module.dag is not None

    def test_scraping_dag_tasks(self):
        """Test scraping DAG has correct tasks"""
        assert hasattr(self.dag_module, "scrape_task")
        assert hasattr(self.dag_module, "datalake_insert_task")
        assert hasattr(self.dag_module, "cleanup_task")


class TestDbtPipeline:
    """Tests for the dbt pipeline DAG"""

    def setup_method(self):
        # Mock Airflow modules
        mock_airflow = MagicMock()
        mock_bash_operator = MagicMock()

        sys.modules["airflow"] = mock_airflow
        sys.modules["airflow.models"] = mock_airflow.models
        sys.modules["airflow.operators"] = mock_airflow.operators
        sys.modules["airflow.operators.bash"] = mock_bash_operator

        # Mock dotenv
        sys.modules["dotenv"] = MagicMock()

        sys.path.insert(0, "airflow/dags")
        self.dag_module = __import__("dbt_pipeline")

    def test_dbt_dag_loaded(self):
        """Test that dbt DAG is loaded"""
        assert self.dag_module.dag is not None

    def test_dbt_dag_tasks(self):
        """Test dbt DAG has correct tasks"""
        assert hasattr(self.dag_module, "dbt_run_staging")
        assert hasattr(self.dag_module, "dbt_snapshot")
        assert hasattr(self.dag_module, "dbt_build")

    def test_dbt_env_variables(self):
        """Test dbt environment variables are configured"""
        assert hasattr(self.dag_module, "DBT_ENV")
        # DBT_ENV should contain necessary paths
        assert self.dag_module.DBT_ENV is not None


class TestUtils:
    """Tests for utility functions used in DAGs"""

    def setup_method(self):
        sys.path.insert(0, "airflow/dags")
        self.utils = __import__("utils")

    def test_scrape_daily_data_function_exists(self):
        """Test scrape_daily_data function exists in utils"""
        assert hasattr(self.utils, "scrape_daily_data")

    def test_insert_into_datalake_function_exists(self):
        """Test insert_into_datalake function exists in utils"""
        assert hasattr(self.utils, "insert_into_datalake")

    def test_cleanup_old_files_function_exists(self):
        """Test cleanup_old_files function exists in utils"""
        assert hasattr(self.utils, "cleanup_old_files")

    def test_scrape_daily_data_filename_format(self):
        """Test that scrape_daily_data generates correct filename"""
        test_date = datetime(2024, 1, 15, 10, 0, 0)
        context = {"ds": "2024-01-15", "logical_date": test_date}

        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 0

            result = self.utils.scrape_daily_data(**context)
            expected_filename = "/opt/airflow/data/scraped_jobs_2024-01-15.csv"

            assert "2024-01-15" in result
            assert result.endswith(".csv")
            assert result == expected_filename

    def test_scrape_daily_data_failure_handling(self):
        """Test that scrape_daily_data handles failures properly"""
        with patch("subprocess.run") as mock_subprocess:
            mock_subprocess.return_value.returncode = 1

            context = {"ds": "2024-01-15", "logical_date": datetime(2024, 1, 15)}

            with pytest.raises(Exception) as exc_info:
                self.utils.scrape_daily_data(**context)

            assert "Scraping failed" in str(exc_info.value)
