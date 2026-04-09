from pathlib import Path
from transformers import MarianMTModel, MarianTokenizer
from progress_tracker import ProgressTracker
import time

tracker = ProgressTracker()

MODEL_NAME = "Helsinki-NLP/opus-mt-en-ru"

print("🔄 Loading translation model...")
tokenizer = MarianTokenizer.from_pretrained(MODEL_NAME)
model = MarianMTModel.from_pretrained(MODEL_NAME)
print("✅ Model loaded")


def translate_text(texts, batch_size=8):
    results = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        tokens = tokenizer(batch, return_tensors="pt", padding=True, truncation=True)
        generated = model.generate(**tokens)

        decoded = [tokenizer.decode(t, skip_special_tokens=True) for t in generated]
        results.extend(decoded)

    return results


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


def translate_srt_file(srt_path: Path) -> str:
    try:
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

            translated_text = translate_text(text_lines)

            translated_lines.append(index + "\n")
            translated_lines.append(time_range + "\n")

            for line in translated_text:
                for subline in line.split("\n"):
                    translated_lines.append(subline.strip() + "\n")

            translated_lines.append("\n")

        translated_path = srt_path.with_name(srt_path.stem + ".RU.srt")

        with open(translated_path, "w", encoding="utf-8") as f:
            f.writelines(translated_lines)

        tracker.mark_done("translate", srt_path)
        return f"✅ Translated: {srt_path.name}"

    except Exception as e:
        return f"❌ Error translating {srt_path.name}: {e}"


def main():
    start = time.time()

    all_srts = list(set(Path(".").rglob("*.srt")))
    remaining = []

    for p in all_srts:
        if p.name.endswith(".RU.srt"):
            continue

        ru_srt = p.with_name(p.stem + ".RU.srt")

        if ru_srt.exists():
            if not tracker.is_done("translate", p):
                tracker.mark_done("translate", p)
            continue

        if not tracker.is_done("translate", p):
            remaining.append(p)

    print(f"📁 Found {len(all_srts)} .srt files. {len(remaining)} to translate.")

    success, fail = 0, 0

    for idx, srt in enumerate(remaining, 1):
        print(f"🌍 [{idx}/{len(remaining)}] {srt.name}")
        result = translate_srt_file(srt)
        print(result)

        if result.startswith("✅"):
            success += 1
        else:
            fail += 1

    print(f"\n✅ Success: {success}")
    print(f"❌ Failed:  {fail}")
    print(f"⏱️ Time: {time.time() - start:.1f} sec")


if __name__ == "__main__":
    main()