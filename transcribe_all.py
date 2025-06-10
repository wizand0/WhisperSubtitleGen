import argparse
from pathlib import Path
from faster_whisper import WhisperModel
import subprocess
from progress_tracker import ProgressTracker

SUPPORTED_EXTENSIONS = [
    ".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm",
    ".mp3", ".m4a", ".aac", ".ogg"
]

tracker = ProgressTracker()

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
            f.write(f"{i}\n{format_timestamp(segment.start)} --> {format_timestamp(segment.end)}\n{segment.text.strip()}\n\n")

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
    return [p for ext in SUPPORTED_EXTENSIONS for p in root.rglob(f"*{ext}")]

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
        print("❌ CUDA initialization error:")
        print(f"    {e}")
        print("💡 Try again using --device cpu")
        return

    all_videos = find_videos(Path("."))
    remaining = [v for v in all_videos if not tracker.is_done("transcribe", v)]
    print(f"📁 Found {len(all_videos)} media files. {len(remaining)} to process.")

    for idx, video in enumerate(remaining, 1):
        print(f"🎧 [{idx}/{len(remaining)}] Processing: {video.name}")
        try:
            transcribe_video(model, video, args.lang, args.batch_size, args.device)
            tracker.mark_done("transcribe", video)
        except Exception as e:
            print(f"❌ Error processing {video.name}: {e}")

if __name__ == "__main__":
    main()