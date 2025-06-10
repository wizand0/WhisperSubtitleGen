@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ⚙️ Выбор модели
set MODEL_SIZE=base
set LANGUAGE=ru

REM 🧾 Можно изменить выше на: medium / large-v2 и язык en/ru/etc

echo 🔧 Используется модель: %MODEL_SIZE%, язык: %LANGUAGE%

REM 🧪 Создание окружения
if not exist .venv (
    echo 🐍 Создание виртуального окружения...
    python -m venv .venv
)

REM 🔄 Активация
call .venv\Scripts\activate.bat

REM 📦 Установка зависимостей
echo 📦 Установка зависимостей...
pip install --upgrade pip >nul
pip install -r requirements.txt >nul 2>nul

REM ▶ Запуск Python-скрипта с параметрами
echo 🚀 Запуск генерации субтитров...
python transcribe_recursive.py %MODEL_SIZE% %LANGUAGE%

echo ✅ Обработка завершена. Лог: transcribe.log
pause
