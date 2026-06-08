FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir uv && uv pip install --system --no-cache -r pyproject.toml

# Copy backend source
COPY backend/ .

# Copy RAG data from project root
COPY zi_wei_dou_shu_rag_chunks.json /app/data/zi_wei_dou_shu_rag_chunks.json

RUN chmod +x start.sh

ENV RAG_DATA_PATH=/app/data/zi_wei_dou_shu_rag_chunks.json
ENV RAG_VECTOR_DB_PATH=/app/data/vector_db

EXPOSE 8000

CMD ["./start.sh"]
