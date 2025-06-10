from pathlib import Path
from transformers import pipeline
from progress_tracker import ProgressTracker

tracker = ProgressTracker()

def translate_text(texts, translator):
    return [translator(text)[0]["translation_text"] for text in texts]

def split_srt_blocks(lines):
    blocks = []
    current = []
    for line in lines:
        if line.strip() == "":
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)
    return blocks

def translate_srt(srt_path: Path, translator):
    with open(srt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    blocks = split_srt_blocks(lines)
    translated_lines = []

    for block in blocks:
        if len(block) < 3:
            translated_lines.extend(block + ["\n"])
            continue

        index = block[0].strip()
        time_range = block[1].strip()
        text_lines = [line.strip() for line in block[2:]]

        translated_text = translate_text(text_lines, translator)

        translated_lines.append(index + "\n")
        translated_lines.append(time_range + "\n")
        translated_lines.extend(line + "\n" for line in translated_text)
        translated_lines.append("\n")

    translated_path = srt_path.with_name(srt_path.stem + ".translated.srt")
    with open(translated_path, "w", encoding="utf-8") as f:
        f.writelines(translated_lines)

    print(f"✅ Translated: {translated_path.name}")

def main():
    print("📦 Loading translation model...")
    translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-ru")

    all_srts = list(Path(".").rglob("*.srt"))
    remaining = [p for p in all_srts if ".translated.srt" not in p.name and not tracker.is_done("translate", p)]

    print(f"📁 Found {len(all_srts)} .srt files. {len(remaining)} to translate.")

    for idx, srt_path in enumerate(remaining, 1):
        print(f"🌍 [{idx}/{len(remaining)}] Translating: {srt_path.name}")
        try:
            translate_srt(srt_path, translator)
            tracker.mark_done("translate", srt_path)
        except Exception as e:
            print(f"❌ Error translating {srt_path.name}: {e}")

if __name__ == "__main__":
    main()