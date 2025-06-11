import os
import hashlib
import subprocess
from pathlib import Path
import pysrt
import tempfile
import argparse
from progress_tracker import ProgressTracker

VOICEOVER_SECTION = "voiceover"
TEMP_DIR = Path(tempfile.gettempdir()) / "whisper_voiceover"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

VOICE_MAP = {
    "male": "ru-RU-DmitryNeural",
    "female": "ru-RU-SvetlanaNeural"
}

def text_to_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def synthesize_tts(text: str, output_path: Path, voice: str):
    subprocess.run([
        "edge-tts",
        "--text", text,
        "--voice", voice,
        "--write-media", str(output_path)
    ], check=True)

def generate_voiceover(voice_gender: str, replace_original: bool):
    tracker = ProgressTracker()
    voice = VOICE_MAP.get(voice_gender.lower(), "ru-RU-DmitryNeural")

    for srt_file in Path(".").rglob("*.RU.srt"):
        video_file = Path(srt_file.name.replace(".RU.srt", ".mp4")).resolve()
        if not video_file.exists():
            print(f"⚠️ Video not found for: {srt_file.name}")
            continue

        if tracker.is_done(VOICEOVER_SECTION, video_file):
            print(f"✅ Already done: {video_file.name}")
            continue

        print(f"\n🎙️ Generating voiceover for: {video_file.name}")

        try:
            subs = pysrt.open(srt_file, encoding='utf-8')
            full_text = " ".join(sub.text.replace("\n", " ").strip() for sub in subs if sub.text.strip())
            if not full_text:
                print("❌ No text to synthesize.")
                continue

            voice_hash = text_to_hash(full_text + voice)
            tts_wav = TEMP_DIR / f"{voice_hash}.wav"
            if not tts_wav.exists():
                print("🗣️ Synthesizing with edge-tts...")
                synthesize_tts(full_text, tts_wav, voice)

            # Уменьшаем громкость оригинального звука
            original_quiet = TEMP_DIR / (video_file.stem + ".quiet.aac")
            subprocess.run([
                "ffmpeg", "-y", "-i", str(video_file),
                "-map", "0:a:0",
                "-filter:a", "volume=0.10",
                "-c:a", "aac", str(original_quiet)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Объединяем дорожки
            temp_output_path = video_file.with_name(video_file.stem + ".with_audio_tracks.temp.mp4")
            final_output_path = video_file if replace_original else video_file.with_name(video_file.stem + ".with_audio_tracks.mp4")

            subprocess.run([
                "ffmpeg", "-y",
                "-i", str(video_file),
                "-i", str(original_quiet),
                "-i", str(tts_wav),
                "-map", "0:v", "-map", "1:a", "-map", "2:a",
                "-metadata:s:a:0", "language=eng",
                "-metadata:s:a:1", "language=rus",
                "-c:v", "copy", "-c:a", "aac",
                "-shortest", str(temp_output_path)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if replace_original:
                try:
                    os.remove(video_file)
                except FileNotFoundError:
                    pass
                temp_output_path.rename(video_file)
                print(f"✅ Voiceover saved: {video_file.name}")
            else:
                temp_output_path.rename(final_output_path)
                print(f"✅ Voiceover saved: {final_output_path.name}")

            tracker.mark_done(VOICEOVER_SECTION, video_file)

        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gender", type=str, default="male", help="Voice gender: male/female")
    parser.add_argument("--replace", type=str, default="no", help="Replace original file (yes/no)")
    args = parser.parse_args()
    generate_voiceover(args.gender, args.replace.lower() == "yes")
