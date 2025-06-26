import argparse
import multiprocessing
import psutil
import time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from progress_tracker import ProgressTracker
from faster_whisper import WhisperModel
import subprocess

SUPPORTED_EXTENSIONS = [
    ".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv", ".webm",
    ".mp3", ".m4a", ".aac", ".ogg"
]

def extract_audio(video_path: Path, audio_path: Path):
    subprocess.run(
        f'ffmpeg -y -i "{video_path}" -ar 16000 -ac 1 -c:a pcm_s16le "{audio_path}"',
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

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

def transcribe_single(video_path: Path, model_size, lang, batch_size, device) -> str:
    audio_path = video_path.with_suffix(".wav")
    try:
        extract_audio(video_path, audio_path)
        model = WhisperModel(
            model_size,
            device=device,
            compute_type="int8" if device == "cpu" else "float16"
        )
        segments, _ = model.transcribe(
            str(audio_path),
            language=lang,
            beam_size=3,
            task="transcribe"
        )
        segments = list(segments)
        if not segments:
            return f"⚠️ No speech recognized in: {video_path.name}"
        srt_path = video_path.with_suffix(".srt")
        write_srt(segments, srt_path)
        return f"✅ Created: {srt_path.name}"
    except Exception as e:
        return f"❌ Error processing {video_path.name}: {e}"
    finally:
        if audio_path.exists():
            audio_path.unlink()

def find_videos(root: Path):
    return [p for ext in SUPPORTED_EXTENSIONS for p in root.rglob(f"*{ext}")]

def get_auto_worker_count(model_name: str) -> int:
    total_cores = multiprocessing.cpu_count()
    total_ram_gb = psutil.virtual_memory().total / 1024**3

    # RAM footprint estimation per model (realistic avg)
    ram_per_worker = {
        "base": 0.7,
        "small": 1.2,
        "medium": 1.8,
        "large-v2": 2.9,
    }

    per_worker_gb = ram_per_worker.get(model_name, 1.0)
    max_by_ram = int(total_ram_gb / (per_worker_gb * 1.6))  # 20% запас

    # Use up to N cores, but don’t exceed memory limits
    return max(1, min(total_cores, max_by_ram))

def main():
    start_time = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="base")
    parser.add_argument("--lang", default="en")
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--workers", type=int, default=None, help="Number of parallel processes (auto if not set)")
    args = parser.parse_args()

    if args.workers is None:
        args.workers = get_auto_worker_count(args.model)

    print(f"⚙️ Using {args.workers} parallel workers")

    tracker = ProgressTracker()
    all_videos = find_videos(Path("."))
    remaining = [v for v in all_videos if not tracker.is_done("transcribe", v)]

    print(f"📁 Found {len(all_videos)} media files. {len(remaining)} to process.")
    for idx, v in enumerate(remaining, 1):
        print(f"   {idx:02d}) {v.name}")

    success_count = 0
    fail_count = 0

    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                transcribe_single, video, args.model, args.lang, args.batch_size, args.device
            ): video for video in remaining
        }

        print("\n🚀 Processing started...\n")
        for idx, future in enumerate(as_completed(futures), 1):
            video = futures[future]
            print(f"🔄 [{idx}/{len(remaining)}] Waiting for: {video.name}")
            try:
                result = future.result()
                print(f"🎧 [{idx}/{len(remaining)}] {result}")
                if result.startswith("✅"):
                    tracker.mark_done("transcribe", video)
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                print(f"❌ Failed processing {video.name}: {e}")
                fail_count += 1

    duration = time.time() - start_time
    print("\n📝 Summary:")
    print(f"   ✅ Success: {success_count}")
    print(f"   ❌ Failed:  {fail_count}")
    print(f"⏱️ Total time: {duration:.1f} seconds ({duration/60:.2f} min)")

if __name__ == "__main__":
    main()
