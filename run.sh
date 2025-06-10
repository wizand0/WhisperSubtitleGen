#!/bin/bash
export LC_ALL=C.UTF-8

# ✅ Запрос параметров у пользователя
read -p "Model (base / small / medium / large-v2): " MODEL_SIZE
read -p "Language (e.g., en or ru): " LANGUAGE
read -p "Batch size (default 16): " BATCH_SIZE
read -p "Device (cuda / cpu): " DEVICE
read -p "Translate to Russian after transcription? (yes/no): " TRANSLATE

# Установка значения по умолчанию
if [ -z "$BATCH_SIZE" ]; then
  BATCH_SIZE=16
fi

echo "🔧 Model: $MODEL_SIZE, Language: $LANGUAGE, Device: $DEVICE, Translate: $TRANSLATE"

# 🧪 Создание виртуального окружения
if [ ! -d ".venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv .venv
fi

# 🔁 Активация окружения
source .venv/bin/activate

# 📥 Установка зависимостей
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 🧠 Запуск распознавания речи
echo "🎙️ Starting transcription..."
python transcribe_all.py --model "$MODEL_SIZE" --lang "$LANGUAGE" --batch_size "$BATCH_SIZE" --device "$DEVICE"

# 🌍 Перевод субтитров
if [[ "$TRANSLATE" =~ ^([Yy][Ee][Ss]|[Дд][Аа])$ ]]; then
  echo "🌍 Installing translation tools..."
  pip install transformers sentencepiece
  echo "📝 Translating .srt files..."
  python translate_srt.py
fi

echo "✅ Done."
