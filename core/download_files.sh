#!/bin/sh

set -e

echo "🚀 Starting download of static files (Alpine Mode)..."
mkdir -p data/dolphin/models
mkdir -p data/dolphin/assets

download_with_retry() {
    local url="$1"
    local output="$2"
    local max_attempts=3
    local attempt=1
    
    if [ -f "$output" ]; then
        echo "⏭️  $(basename "$output") already exists, skipping download..."
        return 0
    fi
    
    while [ $attempt -le $max_attempts ]; do
        echo "🔄 Attempt $attempt/$max_attempts: Downloading $(basename "$output")..."
        
        if wget -O "$output" "$url"; then
            echo "✅ Successfully downloaded $(basename "$output")"
            return 0
        else
            echo "❌ Failed to download $(basename "$output") (attempt $attempt/$max_attempts)"
            if [ $attempt -eq $max_attempts ]; then
                echo "💥 All download attempts failed for $url"
                return 1
            fi
            attempt=$((attempt + 1))
            echo "⏳ Waiting 5 seconds before retry..."
            sleep 5
        fi
    done
}

echo "🤖 Downloading Dolphin ASR models..."

echo "📥 Downloading Dolphin base model..."
download_with_retry \
    "https://huggingface.co/DataoceanAI/dolphin-base/resolve/main/base.pt" \
    "data/dolphin/models/base.pt"

echo "📥 Downloading Dolphin small model..."
download_with_retry \
    "https://huggingface.co/DataoceanAI/dolphin-small/resolve/main/small.pt" \
    "data/dolphin/models/small.pt"

echo "📥 Downloading Dolphin BPE model..."
download_with_retry \
    "https://huggingface.co/DataoceanAI/dolphin-base/resolve/main/bpe.model" \
    "data/dolphin/assets/bpe.model"

echo "📥 Downloading Dolphin config..."
download_with_retry \
    "https://huggingface.co/DataoceanAI/dolphin-base/resolve/main/config.yaml" \
    "data/dolphin/assets/config.yaml"

echo "📥 Downloading Dolphin feature stats..."
download_with_retry \
    "https://huggingface.co/DataoceanAI/dolphin-base/resolve/main/feats_stats.npz" \
    "data/dolphin/assets/feats_stats.npz"

echo "🎉 Dolphin ASR models download process completed!"
echo "📊 Download summary:"
echo "   - Dolphin ASR models: ✅"
echo "   - Dolphin assets: ✅"  
echo ""
echo "ℹ️  Note: Piper TTS models are now downloaded by the tts-service container"
echo "🚀 You can now run the application!"
