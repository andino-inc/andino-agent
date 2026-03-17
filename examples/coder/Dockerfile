FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml /sdk/
COPY src/ /sdk/src/
RUN pip install --no-cache-dir /sdk[bedrock] && rm -rf /sdk

COPY examples/coder/ .

CMD ["python", "-m", "andino", "agent.yaml"]
