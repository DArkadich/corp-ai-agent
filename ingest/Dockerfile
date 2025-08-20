FROM python:3.11-slim
RUN apt-get update && apt-get install -y poppler-utils && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY ingest/ingest.py .
RUN pip install --no-cache-dir sqlalchemy psycopg2-binary pgvector requests pymupdf
CMD ["python","ingest.py"]
