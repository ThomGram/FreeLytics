import pandas as pd
import pytest


class TestJobAnalyzer:
    """Test suite for job analytics functionality using TDD approach."""

    @pytest.fixture
    def sample_job_data(self):
        """Sample job data for testing analytics."""
        return pd.DataFrame(
            {
                "job_title": [
                    "Data Scientist",
                    "Python Developer",
                    "DevOps Engineer",
                    "Data Analyst",
                    "Full Stack Developer",
                ],
                "job_category": ["Data Science", "Backend", "DevOps", "Data Science", "Full Stack"],
                "company_location": [
                    "Paris, France",
                    "Lyon, France",
                    "Paris, France",
                    "Marseille, France",
                    "Toulouse, France",
                ],
                "company_size": [
                    "100 - 249 salariés",
                    "< 20 salariés",
                    "> 1 000 salariés",
                    "250 - 999 salariés",
                    "50 - 99 salariés",
                ],
                "company_type": ["ESN", "Startup", "ESN", "Cabinet de recrutement", "ESN"],
                "contract_CDI": [True, False, True, True, False],
                "contract_Freelance": [False, True, False, False, True],
                "salary_min": ["45000", "50000", "", "40000", "48000"],
                "salary_max": ["55000", "60000", "", "45000", "55000"],
                "daily_rate_min": ["", "400", "500", "", "450"],
                "daily_rate_max": ["", "500", "600", "", "550"],
                "remote_work": ["Hybride", "Full Remote", "Présentiel", "Hybride", "Full Remote"],
                "start_date_asap": [True, False, True, False, False],
                "publication_date": [
                    pd.Timestamp("2024-01-15"),
                    pd.Timestamp("2024-01-20"),
                    pd.Timestamp("2024-01-10"),
                    pd.Timestamp("2024-01-25"),
                    pd.Timestamp("2024-01-18"),
                ],
                "start_date": [
                    pd.NaT,
                    pd.Timestamp("2024-03-01"),
                    pd.NaT,
                    pd.Timestamp("2024-02-15"),
                    pd.Timestamp("2024-02-20"),
                ],
                "duration_days": [365.0, 180.0, 730.0, 365.0, 270.0],
                "skills": [
                    "Python, SQL, Machine Learning",
                    "Python, Django, PostgreSQL",
                    "Docker, Kubernetes, AWS",
                    "SQL, Tableau, Excel",
                    "React, Node.js, MongoDB",
                ],
                "experience_required": ["3-5 ans", "Junior", "5+ ans", "1-3 ans", "2-4 ans"],
            }
        )
