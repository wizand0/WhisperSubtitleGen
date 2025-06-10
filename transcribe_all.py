# transcribe_all.py
import os
import argparse
from pathlib import Path
from faster_whisper import WhisperModel
import subprocess

def extract_audio(video_path: Path, audio_path: Path):
    subprocess.run([
        "ffmpeg", "-y", "-i", str(video_path),
        "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(audio_path)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def write_srt(segments, srt_path: Path):
    def format_timestamp(seconds):
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

    with open(srt_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(segments, 1):
            start = format_timestamp(segment.start)
            end = format_timestamp(segment.end)
            f.write(f"{i}\n{start} --> {end}\n{segment.text.strip()}\n\n")

def transcribe_video(model, video_path: Path, lang, batch_size, device):
    audio_path = video_path.with_suffix(".wav")
    try:
        extract_audio(video_path, audio_path)

        segments, _ = model.transcribe(
            str(audio_path),
            language=lang,
            beam_size=5,
            task="transcribe"
        )

        segments = list(segments)
        if not segments:
            print(f"⚠️ No speech recognized in: {video_path.name}")
            return

        srt_path = video_path.with_suffix(".srt")
        write_srt(segments, srt_path)
        print(f"✅ Created: {srt_path.name}")
    finally:
        if audio_path.exists():
            audio_path.unlink()

def find_videos(root: Path):
    return [p for p in root.rglob("*.mp4")]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="base")
    parser.add_argument("--lang", default="en")
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    args = parser.parse_args()

    print(f"📦 Loading Whisper model: {args.model} on {args.device}")
    try:
        model = WhisperModel(
            args.model,
            device=args.device,
            compute_type="int8" if args.device == "cpu" else "float16"
        )
    except RuntimeError as e:
        print("❌ Ошибка при инициализации модели на CUDA:")
        print(f"    {e}")
        print("💡 Возможно, ваша система не поддерживает CUDA или драйверы не установлены.")
        print("👉 Попробуйте снова, выбрав устройство: cpu")
        return

    for video in find_videos(Path(".")):
        print(f"🎧 Processing: {video.name}")
        try:
            transcribe_video(model, video, args.lang, args.batch_size, args.device)
        except Exception as e:
            print(f"❌ Error processing {video.name}: {e}")

if __name__ == "__main__":
    main()