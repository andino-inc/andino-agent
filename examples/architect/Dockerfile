FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml src/ /sdk/
RUN pip install --no-cache-dir /sdk[bedrock] && rm -rf /sdk

COPY examples/architect/ .

CMD ["python", "-m", "andino", "agent.yaml"]
