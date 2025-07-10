# syntax=docker.io/docker/dockerfile:1.7-labs
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    wget \
    curl \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY data/ ./data/
RUN mkdir -p data/dolphin/models data/dolphin/assets && \
    if [ ! -f "data/dolphin/models/base.pt" ]; then \
    echo "Downloading base.pt model..."; \
    wget -O data/dolphin/models/base.pt "https://huggingface.co/DataoceanAI/dolphin-base/resolve/main/base.pt"; \
    fi && \
    if [ ! -f "data/dolphin/models/small.pt" ]; then \
    echo "Downloading small.pt model..."; \
    wget -O data/dolphin/models/small.pt "https://huggingface.co/DataoceanAI/dolphin-small/resolve/main/small.pt"; \
    fi && \
    if [ ! -f "data/dolphin/assets/bpe.model" ]; then \
    echo "Downloading bpe.model..."; \
    wget -O data/dolphin/assets/bpe.model "https://huggingface.co/DataoceanAI/dolphin-base/resolve/main/bpe.model"; \
    fi && \
    if [ ! -f "data/dolphin/assets/config.yaml" ]; then \
    echo "Downloading config.yaml..."; \
    wget -O data/dolphin/assets/config.yaml "https://huggingface.co/DataoceanAI/dolphin-base/resolve/main/config.yaml"; \
    fi && \
    if [ ! -f "data/dolphin/assets/feats_stats.npz" ]; then \
    echo "Downloading feats_stats.npz..."; \
    wget -O data/dolphin/assets/feats_stats.npz "https://huggingface.co/DataoceanAI/dolphin-base/resolve/main/feats_stats.npz"; \
    fi

# COPY wheels/ ./wheels/
# RUN pip install --no-cache-dir --trusted-host https://pypi.tuna.tsinghua.edu.cn -i https://pypi.tuna.tsinghua.edu.cn/simple/ ./wheels/*.whl && rm -rf ./wheels/
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get purge -y gcc g++ build-essential wget && \
    apt-get autoremove -y && \
    apt-get clean

# COPY --exclude=wheels  . .
COPY . .

RUN useradd -m -u 1000 asruser && \
    chown -R asruser:asruser /app
USER asruser

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

CMD ["python", "main.py"]
