#!/bin/sh

set -e

echo "🚀 Starting download of static files (Alpine Mode)..."

echo "📁 Creating directories..."
mkdir -p data/dolphin/models
mkdir -p data/dolphin/assets
mkdir -p data/piper/models
mkdir -p data/piper

download_with_retry() {
    local url="$1"
    local output="$2"
    local max_attempts=3
    local attempt=1
    
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

gdown_with_retry() {
    local file_id="$1"
    local output="$2"
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "🔄 Attempt $attempt/$max_attempts: Downloading $(basename "$output") via gdown..."
        
        if gdown "$file_id" -O "$output"; then
            echo "✅ Successfully downloaded $(basename "$output")"
            return 0
        else
            echo "❌ Failed to download $(basename "$output") (attempt $attempt/$max_attempts)"
            if [ $attempt -eq $max_attempts ]; then
                echo "💥 All download attempts failed for file ID: $file_id"
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

echo "🎤 Downloading Piper TTS models..."

echo "📥 Downloading Piper voices configuration..."
download_with_retry \
    "https://huggingface.co/rhasspy/piper-voices/raw/v1.0.0/voices.json" \
    "data/piper/voices.json"

echo "📥 Downloading Piper voice models (this may take a while)..."
gdown_with_retry \
    "13pxf4H0-2phQVUe_Cyvdvg5SKKaSL2tc" \
    "piper_voices.zip"

echo "📦 Extracting Piper voice models..."
if unzip -q piper_voices.zip -d data/piper/models/; then
    echo "✅ Successfully extracted Piper voice models"
    rm piper_voices.zip
    echo "🗑️  Cleaned up zip file"
else
    echo "❌ Failed to extract Piper voice models"
    exit 1
fi

echo "🎉 All static files downloaded successfully!"
echo "📊 Download summary:"
echo "   - Dolphin ASR models: ✅"
echo "   - Dolphin assets: ✅"  
echo "   - Piper TTS voices: ✅"
echo "   - Piper voice models: ✅"
echo ""
echo "🚀 You can now run the application!"
