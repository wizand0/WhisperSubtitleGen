@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set /p MODEL_SIZE=Model (base / small / medium / large-v2):
set /p LANGUAGE=Language (e.g., en or ru):
set /p BATCH_SIZE=Batch size (default 16):
set /p DEVICE=Device (cuda / cpu):
set /p TRANSLATE=Translate to Russian after transcription? (yes/no):

if "%BATCH_SIZE%"=="" set BATCH_SIZE=16

echo Model: %MODEL_SIZE%, Language: %LANGUAGE%, Device: %DEVICE%, Translate: %TRANSLATE%

if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip >nul
pip install -r requirements.txt >nul 2>nul

echo Starting transcription...
python transcribe_all.py --model "%MODEL_SIZE%" --lang "%LANGUAGE%" --batch_size "%BATCH_SIZE%" --device "%DEVICE%"

if /I "%TRANSLATE%"=="yes" (
    echo Starting translation of .srt files...
    pip install transformers sentencepiece >nul 2>nul
    python translate_srt.py
)

echo Done.
pause
