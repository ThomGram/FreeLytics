FROM apache/airflow:3.0.6

USER root

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

USER airflow

COPY pyproject.toml README.md /opt/airflow/
COPY src/ /opt/airflow/src/

RUN uv sync && uv pip install -e .
COPY data/ /opt/airflow/data/
COPY airflow/dags/ /opt/airflow/dags/
COPY FreeLytics.cfg /opt/airflow/

WORKDIR /opt/airflow
