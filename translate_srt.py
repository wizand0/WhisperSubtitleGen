import os
from pathlib import Path
from transformers import MarianMTModel, MarianTokenizer

os.environ["TRANSFORMERS_CACHE"] = str(Path(".cache").resolve())

def read_srt(path):
    blocks = []
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        for block in content.split("\n\n"):
            lines = block.strip().split("\n")
            if len(lines) >= 3:
                blocks.append((lines[0], lines[1], " ".join(lines[2:])))
    return blocks

def write_srt(path, blocks):
    with open(path, "w", encoding="utf-8") as f:
        for i, (idx, ts, text) in enumerate(blocks, 1):
            f.write(f"{i}\n{ts}\n{text.strip()}\n\n")

def translate_texts(texts, model, tokenizer, batch_size=8):
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True)
        output = model.generate(**inputs)
        translated = tokenizer.batch_decode(output, skip_special_tokens=True)
        results.extend(translated)
    return results

def main():
    model_name = "Helsinki-NLP/opus-mt-en-ru"
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)

    for srt_path in Path(".").rglob("*.srt"):
        if srt_path.name.endswith(".ru.srt"):
            continue

        print(f"🌍 Translating: {srt_path.name}")
        blocks = read_srt(srt_path)
        texts = [text for _, _, text in blocks]

        translated = translate_texts(texts, model, tokenizer)
        new_blocks = [(idx, ts, text) for (idx, ts, _), text in zip(blocks, translated)]

        ru_path = srt_path.with_name(srt_path.stem + ".ru.srt")
        write_srt(ru_path, new_blocks)
        print(f"✅ Saved: {ru_path.name}")

if __name__ == "__main__":
    main()
