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

COPY prepare_data.sh .
RUN chmod +x ./prepare_data.sh
RUN ./prepare_data.sh

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir wheels/piper_tts_persian_phonemizer-1.2.0+custom.persian.phonemizer-py3-none-any.whl

RUN apt-get purge -y gcc g++ build-essential wget unzip && \
    apt-get autoremove -y && \
    apt-get clean

COPY . .

RUN useradd -m -u 1000 ttsuser && \
    chown -R ttsuser:ttsuser /app
USER ttsuser

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/api/tts/health || exit 1

CMD ["python", "main.py"]
