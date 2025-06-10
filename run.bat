@echo off
set "VENV_DIR=.venv"
set "PYTHON=python"

:: Создание виртуального окружения, если не существует
if not exist %VENV_DIR% (
    %PYTHON% -m venv %VENV_DIR%
)

:: Активация виртуального окружения
call %VENV_DIR%\Scripts\activate.bat

:: Установка зависимостей
pip install -r requirements.txt

:: Запуск основного скрипта
%PYTHON% generate_subtitles.py

pause
