from pathlib import Path
from transformers import pipeline
from progress_tracker import ProgressTracker
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import time

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

def translate_srt_file(srt_path: Path) -> str:
    try:
        translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-ru")

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

        translated_path = srt_path.with_name(srt_path.stem + ".RU.srt")
        with open(translated_path, "w", encoding="utf-8") as f:
            f.writelines(translated_lines)

        tracker.mark_done("translate", srt_path)
        return f"✅ Translated: {srt_path.name}"
    except Exception as e:
        return f"❌ Error translating {srt_path.name}: {e}"

def main():
    start = time.time()
    all_srts = list(Path(".").rglob("*.srt"))
    remaining = []

    for p in all_srts:
        if ".translated.srt" in p.name:
            continue
        ru_srt = p.with_name(p.stem + ".RU.srt")
        if ru_srt.exists():
            if not tracker.is_done("translate", p):
                tracker.mark_done("translate", p)
            continue
        if not tracker.is_done("translate", p):
            remaining.append(p)

    print(f"📁 Found {len(all_srts)} .srt files. {len(remaining)} to translate.")

    workers = min(multiprocessing.cpu_count(), 4)
    print(f"⚙️ Using {workers} parallel translators")

    success, fail = 0, 0

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(translate_srt_file, srt): srt for srt in remaining}
        for idx, future in enumerate(as_completed(futures), 1):
            print(f"🌍 [{idx}/{len(remaining)}] {futures[future].name}")
            result = future.result()
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
