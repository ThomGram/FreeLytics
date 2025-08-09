FROM apache/airflow:2.10.0-python3.12

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

RUN uv sync

COPY src/ /opt/airflow/src/
COPY data/ /opt/airflow/data/
COPY airflow/dags/ /opt/airflow/dags/

WORKDIR /opt/airflow
