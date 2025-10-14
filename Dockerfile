FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir -e .

CMD ["python", "-m", "tcmb_mcp_server.server"]
