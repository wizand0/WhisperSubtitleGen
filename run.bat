@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ?? Set path to Python 3.10
set PYTHON310="C:\Program Files\Python310\python.exe"

if not exist %PYTHON310% (
    echo ? Python 3.10 not found at %PYTHON310%
    echo Please install it from https://www.python.org/downloads/release/python-3100/
    pause
    exit /b
)

:: ?? Ask model size
echo Available models: base (~142MB), small (~466MB), medium (~1.5GB), large-v2 (~2.9GB)
echo Larger models are more accurate but slower.
set /p MODEL_SIZE=Choose Whisper model (default: base):
if "%MODEL_SIZE%"=="" set MODEL_SIZE=base

:: ?? Language code (for source audio)
echo Language code example: en = English, ru = Russian
set /p LANGUAGE=Language code of source audio (default: en):
if "%LANGUAGE%"=="" set LANGUAGE=en

:: ?? Batch size affects memory usage
echo Batch size (default 16). Lower it if you face memory issues.
set /p BATCH_SIZE=Batch size (default: 16):
if "%BATCH_SIZE%"=="" set BATCH_SIZE=16

:: ??? Choose device
echo Device options: cuda = GPU (faster), cpu = CPU (slower)
set /p DEVICE=Device to use (default: cpu):
if "%DEVICE%"=="" set DEVICE=cpu

:: ?? Translation option
echo Translate subtitles to Russian after transcription?
set /p TRANSLATE=Translate to Russian after transcription? (yes/no, default: no):
if "%TRANSLATE%"=="" set TRANSLATE=no

set VOICEOVER=no
set VOICE_GENDER=male
set VOICEOVER_REPLACE=no

:: ?? Ask about voiceover only if translation is enabled
if /I "%TRANSLATE%"=="yes" goto ask_voiceover
goto continue_script

:ask_voiceover
echo You can generate Russian voiceover from translated subtitles.
echo WARNING: This will use internet traffic (~1MB per minute of audio).
set /p VOICEOVER=Do you want to generate Russian voiceover? (yes/no, default: no):
if "%VOICEOVER%"=="" set VOICEOVER=no
if /I "%VOICEOVER%"=="yes" goto ask_gender
goto continue_script

:ask_gender
echo Choose voice gender for TTS: male or female
set /p VOICE_GENDER=Which voice? (male/female, default: male):
if "%VOICE_GENDER%"=="" set VOICE_GENDER=male

echo If you choose yes, original .mp4 will be replaced with a new one (with extra audio track)
set /p VOICEOVER_REPLACE=Replace original .mp4 file? (yes/no, default: no):
if "%VOICEOVER_REPLACE%"=="" set VOICEOVER_REPLACE=no
goto continue_script

:continue_script
echo.
echo Model: %MODEL_SIZE%
echo Language: %LANGUAGE%
echo Device: %DEVICE%
echo Batch size: %BATCH_SIZE%
echo Translate: %TRANSLATE%
echo Voiceover: %VOICEOVER%
echo Voice gender: %VOICE_GENDER%
echo Replace video: %VOICEOVER_REPLACE%
echo.

if not exist .venv (
    echo ?? Creating virtual environment using Python 3.10...
    %PYTHON310% -m venv .venv
)

call .venv\Scripts\activate.bat

:: ?? Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt >nul 2>nul

:: ?? Start transcription
echo Starting transcription...
python transcribe_all.py --model "%MODEL_SIZE%" --lang "%LANGUAGE%" --batch_size "%BATCH_SIZE%" --device "%DEVICE%"

:: ?? Translate subtitles if enabled
if /I "%TRANSLATE%"=="yes" (
    echo Starting translation of .srt files...
    pip install transformers sentencepiece >nul 2>nul
    python translate_srt.py
)

:: ?? Voiceover generation
if /I "%VOICEOVER%"=="yes" (
    echo Installing voiceover dependencies...
    pip install edge-tts pysrt >nul 2>nul
    echo Starting voiceover generation...
    python voiceover_srt.py --gender "%VOICE_GENDER%" --replace "%VOICEOVER_REPLACE%"
)

echo.
echo ? Done.
pause
