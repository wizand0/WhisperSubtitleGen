
# 🎧 WhisperSubtitleGen

## ** В новой версии Онлайн генерация РУССКОЙ ОЗВУЧКИ**
## ** ATTENTION!!! You need ONLY Python 3.10! Only this version, NOT OTHER**
## ** Внимание!!! Версия Python 3.10! Только эта версия нужна, другие не подойдут!**

> **Automatic `.srt` subtitle generation for offline videos using Faster-Whisper — fully offline.**  
> **Автоматическая генерация субтитров `.srt` для офлайн-видео с помощью Faster-Whisper — полностью офлайн.**


---

## 📌 About / О проекте

This tool processes a large archive of **offline videos** to improve understanding and productivity during review. It generates `.srt` subtitles for each video file found in a folder and subfolders.  
Этот инструмент предназначен для обработки большого архива **офлайн-видео** и генерации к ним `.srt` субтитров, что помогает лучше понимать материал и пересматривать видео.

** ATTENTION!!! You need ONLY Python 3.10! Only this version, NOT OTHER**

It uses [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) and works **completely offline**. The subtitles are saved next to each video, allowing automatic loading in players like VLC.  
Используется [Faster-Whisper](https://github.com/guillaumekln/faster-whisper), работающий **полностью офлайн**. Субтитры сохраняются рядом с видео и автоматически подгружаются в VLC и других плеерах.

---

## 🆕 New Feature / Новая функция

**✅ Progress tracking and recovery**  
**📌 Отслеживание прогресса и восстановление**

If the script is interrupted (e.g., power loss), it **saves progress** to a temporary file and **resumes** from where it left off on next launch.  
Если выполнение прерывается (например, сбой питания), скрипт **сохраняет прогресс** во временный файл и **возобновляет** обработку с этого места при следующем запуске.

---

## 🧠 Technologies / Используемые технологии

- Faster-Whisper (ONNX + CTranslate2)
- Python 3.10
- ffmpeg (required / обязателен)

---

## 📂 How It Works / Как это работает

1. Recursively scans the current folder and all subfolders  
   Рекурсивно сканирует текущую папку и все подпапки
2. Detects video/audio files (.mp4, .mkv, .avi, .mp3, .wav)  
   Обнаруживает видео и аудиофайлы
3. For each file:  
   Для каждого файла:
   - Transcribes audio / Распознаёт речь
   - Generates `.srt` subtitle in the same folder / Создаёт файл `.srt` рядом
4. Subtitles auto-load in VLC and other players  
   Субтитры автоматически загружаются в медиаплеерах

---

## 📦 Project Structure / Структура проекта

```
WhisperSubtitleGen/
├── transcribe_recursive.py    # Main script / Основной скрипт
├── run_transcribe.bat         # Windows launcher / Запуск на Windows
├── run.sh                     # Linux launcher / Запуск на Linux
├── requirements.txt           # Dependencies / Зависимости
├── transcribe.log             # Log file (created automatically) / Лог-файл
├── progress.txt               # Progress file (auto-managed) / Файл прогресса
```

---

## ⚙️ Install FFmpeg / Установка FFmpeg

### Windows:

1. Download `ffmpeg-release-essentials.zip`:  
   https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to environment **PATH**
4. Test:
   ```bash
   ffmpeg -version
   ```

### Linux:

Install via package manager:
```bash
sudo apt install ffmpeg
# or
sudo pacman -S ffmpeg
```

---

## 💻 How to Run / Как запустить

### ✅ Windows

1. Copy files to your video folder:  
   Скопируй файлы в папку с видео:
   - `run_transcribe.bat`
   - `transcribe_recursive.py`
   - `requirements.txt`
2. Double-click `run_transcribe.bat`
3. Script will:  
   Скрипт:
   - create `.venv` environment  
     создаст виртуальное окружение
   - install dependencies  
     установит зависимости
   - run `transcribe_recursive.py`  
     запустит скрипт
4. `.srt` files will appear next to videos  
   Субтитры появятся рядом с видео

### 🐧 Linux

1. Copy to your video folder:  
   Скопируй:
   - `run.sh`
   - `transcribe_recursive.py`
   - `requirements.txt`
2. Make script executable:  
   Сделай скрипт исполняемым:
   ```bash
   chmod +x run.sh
   ```
3. Run:
   ```bash
   ./run.sh
   ```

---

## 🔧 Configuration / Конфигурация

In `run_transcribe.bat` or `run.sh` you can modify:  
В `run_transcribe.bat` или `run.sh` можно изменить:
```bash
set MODEL_SIZE=medium
set LANGUAGE=ru
```

- Supported languages: `en`, `ru`, `de`, `fr`, `es`, etc.  
  Поддерживаемые языки
- Formats: `.mp4`, `.avi`, `.mkv`, `.mp3`, `.wav`  
  Поддерживаемые форматы
- Subtitles saved **next to the video file**  
  Субтитры сохраняются **рядом с видео**

---

## 🧪 Checking Results / Проверка результата

1. `.srt` files appear in the same folders  
   Файлы `.srt` появятся в папках с видео
2. Open video in VLC — subtitles load automatically  
   Открой видео в VLC — субтитры загрузятся
3. Or choose manually:  
   Или выбери вручную:  
   Subtitles → Track 1 → Auto-detected

---

## 🧰 Dependencies / Зависимости

Declared in `requirements.txt`:  
Указаны в `requirements.txt`:
```
faster-whisper==1.1.0
```
Model is downloaded on first use and cached.  
Модель скачивается при первом запуске и кэшируется.

---

## 💬 Who Is It For / Кому это может быть полезно

- Students watching lectures / Студентам
- People processing large video archives / Архиваторам
- Anyone needing subtitles without internet / Всем, кому нужны офлайн-субтитры

---

## 📜 License / Лицензия

MIT License
