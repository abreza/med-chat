FROM python:3.10-slim AS builder

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    wget \
    curl \
    git \
    build-essential \
    unzip \
    && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y --no-install-recommends \
    linux-libc-dev \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt piper-req.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-deps -r piper-req.txt

COPY lib/medchatinput/ ./lib/medchatinput/
WORKDIR /app/lib/medchatinput
RUN gradio cc install
RUN gradio cc build

WORKDIR /app

COPY download_files.sh ./
RUN chmod +x download_files.sh && \
    ./download_files.sh

FROM python:3.10-slim AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    libc6-dev \
    linux-libc-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt piper-req.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-deps -r piper-req.txt

RUN apt-get remove -y \
    gcc \
    g++ \
    build-essential \
    libc6-dev \
    linux-libc-dev \
    libffi-dev \
    libssl-dev \
    && apt-get autoremove -y \
    && apt-get clean

COPY --from=builder /app/lib/medchatinput/dist/gradio_medchatinput-0.0.1-py3-none-any.whl ./lib/medchatinput/dist/gradio_medchatinput-0.0.1-py3-none-any.whl
RUN pip install --no-cache-dir ./lib/medchatinput/dist/gradio_medchatinput-0.0.1-py3-none-any.whl

COPY --from=builder /app/data/ ./data/

COPY . .

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 7860

CMD ["python", "main.py"]
