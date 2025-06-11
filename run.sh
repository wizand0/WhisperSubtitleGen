#!/bin/bash

echo "📦 Whisper Subtitle Generator - Linux Launcher"

# Ensure UTF-8 output in terminal
export LANG=en_US.UTF-8

# 🐍 Python path (fallback to 'python3' if not set)
PYTHON_BIN="python3"

# ✅ Choose model
echo "Available models: base (~142MB), small (~466MB), medium (~1.5GB), large-v2 (~2.9GB)"
echo "Larger models are more accurate but slower."
read -p "Choose Whisper model (default: base): " MODEL_SIZE
MODEL_SIZE=${MODEL_SIZE:-base}

# 🌍 Choose language
echo "Language code example: en = English, ru = Russian"
read -p "Language code of source audio (default: en): " LANGUAGE
LANGUAGE=${LANGUAGE:-en}

# 📊 Batch size
echo "Batch size (default: 16). Lower it if you face memory issues."
read -p "Batch size (default: 16): " BATCH_SIZE
BATCH_SIZE=${BATCH_SIZE:-16}

# 🖥️ Choose device
echo "Device options: cuda = GPU (faster), cpu = CPU (slower)"
read -p "Device to use (default: cpu): " DEVICE
DEVICE=${DEVICE:-cpu}

# 🌐 Translate to Russian
read -p "Translate to Russian after transcription? (yes/no, default: no): " TRANSLATE
TRANSLATE=${TRANSLATE:-no}

VOICEOVER="no"
VOICE_GENDER="male"
VOICEOVER_REPLACE="no"

# 🎤 Voiceover setup
if [[ "$TRANSLATE" == "yes" ]]; then
    echo "You can generate Russian voiceover from translated subtitles."
    echo "WARNING: This will use internet traffic (~1MB per minute of audio)."
    read -p "Do you want to generate Russian voiceover? (yes/no, default: no): " VOICEOVER
    VOICEOVER=${VOICEOVER:-no}

    if [[ "$VOICEOVER" == "yes" ]]; then
        read -p "Which voice? (male/female, default: male): " VOICE_GENDER
        VOICE_GENDER=${VOICE_GENDER:-male}

        echo "If you choose yes, original .mp4 will be replaced with a new one (with extra audio track)"
        read -p "Replace original .mp4 file? (yes/no, default: no): " VOICEOVER_REPLACE
        VOICEOVER_REPLACE=${VOICEOVER_REPLACE:-no}
    fi
fi

echo
echo "Model: $MODEL_SIZE"
echo "Language: $LANGUAGE"
echo "Device: $DEVICE"
echo "Batch size: $BATCH_SIZE"
echo "Translate: $TRANSLATE"
echo "Voiceover: $VOICEOVER"
echo "Voice gender: $VOICE_GENDER"
echo "Replace video: $VOICEOVER_REPLACE"
echo

# 🔧 Create virtual env if missing
if [ ! -d ".venv" ]; then
    echo "🧪 Creating virtual environment..."
    $PYTHON_BIN -m venv .venv
fi

# 🧪 Activate virtual environment
source .venv/bin/activate

# 📥 Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null 2>&1

# 📝 Run transcription
echo "📝 Starting transcription..."
python transcribe_all.py --model "$MODEL_SIZE" --lang "$LANGUAGE" --batch_size "$BATCH_SIZE" --device "$DEVICE"

# 🌍 Run translation
if [[ "$TRANSLATE" == "yes" ]]; then
    echo "🌍 Translating subtitles..."
    pip install transformers sentencepiece > /dev/null 2>&1
    python translate_srt.py
fi

# 🎧 Run voiceover
if [[ "$VOICEOVER" == "yes" ]]; then
    echo "🎧 Generating voiceover..."
    pip install edge-tts pysrt > /dev/null 2>&1
    python voiceover_srt.py --gender "$VOICE_GENDER" --replace "$VOICEOVER_REPLACE"
fi

echo
echo "✅ Done."
