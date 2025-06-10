#!/bin/bash
VENV_DIR=".venv"
PYTHON="python3"

# Создание виртуального окружения
if [ ! -d "$VENV_DIR" ]; then
  $PYTHON -m venv $VENV_DIR
fi

# Активация виртуального окружения
source "$VENV_DIR/bin/activate"

# Установка зависимостей
pip install -r requirements.txt

# Запуск основного скрипта
$PYTHON generate_subtitles.py
