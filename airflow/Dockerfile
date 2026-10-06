FROM apache/airflow:2.10.2


COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY --chown=airflow:root pyproject.toml README.md /opt/pipeline-src/
COPY --chown=airflow:root src/ /opt/pipeline-src/src/

# Target Airflow's own interpreter explicitly (no root needed)
RUN uv pip install --python /home/airflow/.local/bin/python --no-cache /opt/pipeline-src