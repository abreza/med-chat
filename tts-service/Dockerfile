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
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir gdown==5.2.0

RUN mkdir -p data/piper/models data/piper && \
    wget -O data/piper/voices.json "https://huggingface.co/rhasspy/piper-voices/raw/v1.0.0/voices.json" && \
    gdown "13pxf4H0-2phQVUe_Cyvdvg5SKKaSL2tc" -O piper_voices.zip && \
    unzip -q piper_voices.zip -d data/piper/models/ && \
    rm piper_voices.zip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get purge -y gcc g++ build-essential wget unzip && \
    apt-get autoremove -y && \
    apt-get clean

COPY . .

RUN useradd -m -u 1000 ttsuser && \
    chown -R ttsuser:ttsuser /app
USER ttsuser

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["python", "main.py"]