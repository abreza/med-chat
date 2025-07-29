#!/bin/bash
set -e

echo "--- Starting data and model preparation ---"

DATA_DIR="data/piper"
MODELS_DIR="${DATA_DIR}/models"
MANA_DIR="${MODELS_DIR}/fa/fa_IR/mana/medium"
WHEEL_DIR="wheels"
EZAFE_ZIP="ezafe_model_quantized.zip"
EZAFE_DIR="ezafe_model_quantized"


mkdir -p "${MANA_DIR}"
mkdir -p "${WHEEL_DIR}"

if [ ! -f "${DATA_DIR}/voices.json" ]; then
  echo "Downloading voices.json..."
  gdown 1PVauqxaGyCsCDthWMVRus0uDsus6D4U1 -O "${DATA_DIR}/voices.json"
else
  echo "voices.json already exists, skipping."
fi

if [ -z "$(ls -A ${MODELS_DIR} 2>/dev/null)" ]; then
  echo "Downloading piper voices..."
  gdown 13pxf4H0-2phQVUe_Cyvdvg5SKKaSL2tc -O piper_voices.zip
  unzip -q piper_voices.zip -d "${MODELS_DIR}/"
  rm piper_voices.zip
else
  echo "Piper models directory not empty, skipping."
fi

if [ ! -f "${MANA_DIR}/fa_IR-mana-medium.onnx" ]; then
  echo "Downloading and processing custom mana voice..."
  gdown 18NM-vFBgNWz217qdlOil3s02Ms2mp1Rw -O mana.zip
  unzip -q mana.zip -d temp_mana_dir
  mv temp_mana_dir/checkpoint*/model.onnx "${MANA_DIR}/fa_IR-mana-medium.onnx"
  mv temp_mana_dir/checkpoint*/model.onnx.json "${MANA_DIR}/fa_IR-mana-medium.onnx.json"
  rm mana.zip
  rm -rf temp_mana_dir
else
  echo "Custom mana voice already exists, skipping."
fi

WHEEL_FILE="${WHEEL_DIR}/piper_tts_persian_phonemizer-1.2.0+custom.persian.phonemizer-py3-none-any.whl"
if [ ! -f "${WHEEL_FILE}" ]; then
  echo "Downloading phonemizer wheel..."
  gdown 1rGYgNsZVOJeKMkwBA3ZdBHdObM0GABW0 -O "${WHEEL_FILE}"
else
  echo "Phonemizer wheel already exists, skipping."
fi

if [ ! -d "${EZAFE_DIR}" ]; then
  echo "Downloading and unzipping ezafe model..."
  gdown 1vdInn73cHsMCszktCqOT1zOtz0ukBwUp -O "${EZAFE_ZIP}"
  unzip -q "${EZAFE_ZIP}" -d ./
  rm "${EZAFE_ZIP}"
else
  echo "Ezafe model directory already exists, skipping."
fi

echo "Updating phoneme type to espeak..."
sed -i 's/"phoneme_type": "custom"/"phoneme_type": "espeak"/g' "${MANA_DIR}/fa_IR-mana-medium.onnx.json"

echo "--- Data preparation complete ✨ ---"