FROM python:3.12-slim

WORKDIR /sdk

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir .[all] && \
    rm -rf /sdk

WORKDIR /app

RUN useradd -m -u 1000 andino
USER andino

ENTRYPOINT ["andino"]
CMD ["--help"]
