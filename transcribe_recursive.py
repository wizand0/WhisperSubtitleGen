import os
import sys
from faster_whisper import WhisperModel
from datetime import datetime

# Параметры из командной строки: модель и язык
model_size = sys.argv[1] if len(sys.argv) > 1 else "base"
language = sys.argv[2] if len(sys.argv) > 2 else None  # например: "ru"

model = WhisperModel(model_size, device="cpu", compute_type="int8")

log = open("transcribe.log", "a", encoding="utf-8")
log.write(f"\n[{datetime.now()}] ▶ Старт: model={model_size}, lang={language or 'auto'}\n")

def format_timestamp(seconds: float):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

supported_exts = (".mp4", ".mp3", ".wav", ".mkv")

for root, _, files in os.walk("."):
    for filename in files:
        if filename.lower().endswith(supported_exts):
            input_path = os.path.join(root, filename)
            output_path = os.path.splitext(input_path)[0] + ".srt"

            if os.path.exists(output_path):
                log.write(f"[{datetime.now()}] ⏭ Уже есть: {output_path}\n")
                continue

            print(f"▶ Обработка: {input_path}")
            log.write(f"[{datetime.now()}] Обработка: {input_path}\n")

            try:
                segments, _ = model.transcribe(input_path, language=language)
                with open(output_path, "w", encoding="utf-8") as srt_file:
                    for i, segment in enumerate(segments, start=1):
                        start = format_timestamp(segment.start)
                        end = format_timestamp(segment.end)
                        text = segment.text.strip()
                        srt_file.write(f"{i}\n{start} --> {end}\n{text}\n\n")

                log.write(f"[{datetime.now()}] ✅ Сохранено: {output_path}\n")
            except Exception as e:
                print(f"❌ Ошибка: {input_path}")
                log.write(f"[{datetime.now()}] ❌ Ошибка: {input_path} — {e}\n")

log.write(f"[{datetime.now()}] 🏁 Завершено\n")
log.close()
