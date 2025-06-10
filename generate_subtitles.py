import os
import subprocess
from pathlib import Path

# Если видео на русском — замени --lang en на --lang ru.

VIDEO_EXTS = ('.mp4', '.mkv', '.avi', '.mov', '.webm')
ROOT = Path(__file__).parent
MODEL = "medium"  # Можно medium, если нужна точность

for path in ROOT.rglob("*"):
    if path.suffix.lower() in VIDEO_EXTS:
        srt_path = path.with_suffix(".srt")
        if srt_path.exists():
            print(f"✅ Уже есть: {srt_path.name}")
            continue

        print(f"🎬 Обработка: {path.name}")
        cmd = [
            "python", "-m", "whisper_live.client",
            str(path),
            "--model", MODEL,
            "--lang", "en",
            "--save_srt_path", str(srt_path),
            "--speed_up"
        ]
        subprocess.run(cmd, check=True)
