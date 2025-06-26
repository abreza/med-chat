FROM python:3.10-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        wget curl git build-essential unzip \
        linux-libc-dev gcc g++ libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

ARG NODE_VERSION=18.20.2
RUN set -eux; \
    ARCH="$(dpkg --print-architecture)"; \

    if [ "$ARCH" = "amd64" ]; then ARCH="x64"; fi; \
    if [ "$ARCH" = "arm64" ]; then ARCH="arm64"; fi; \
    curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${ARCH}.tar.xz" -o node.tar.xz; \
    tar -xf node.tar.xz -C /usr/local --strip-components=1; \
    rm node.tar.xz; \
    node -v && npm -v

WORKDIR /app

COPY requirements.txt piper-req.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --no-deps -r piper-req.txt

COPY lib/medchatinput/ ./lib/medchatinput/
WORKDIR /app/lib/medchatinput
RUN gradio cc install && gradio cc build

WORKDIR /app

COPY download_files.sh ./
RUN chmod +x download_files.sh && ./download_files.sh

FROM python:3.10-slim AS runtime

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg libsndfile1 curl ca-certificates \
        linux-libc-dev gcc g++ build-essential libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt piper-req.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --no-deps -r piper-req.txt

RUN apt-get purge -y gcc g++ build-essential linux-libc-dev libffi-dev libssl-dev && \
    apt-get autoremove -y && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/lib/medchatinput/dist/gradio_medchatinput-0.0.1-py3-none-any.whl ./lib/medchatinput/dist/
RUN pip install --no-cache-dir ./lib/medchatinput/dist/gradio_medchatinput-0.0.1-py3-none-any.whl

COPY --from=builder /app/data/ ./data/

COPY . .

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 7860

CMD ["python", "main.py"]
