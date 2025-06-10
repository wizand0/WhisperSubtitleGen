from pathlib import Path
from collections import defaultdict

PROGRESS_FILE = ".progress.log"

class ProgressTracker:
    def __init__(self, filepath=PROGRESS_FILE):
        self.filepath = Path(filepath)
        self.progress = defaultdict(set)
        self._load()

    def _load(self):
        if not self.filepath.exists():
            return
        current_section = None
        with open(self.filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("[") and line.endswith("]"):
                    current_section = line[1:-1]
                elif current_section and line:
                    self.progress[current_section].add(line)

    def is_done(self, section: str, path: Path) -> bool:
        return str(path.resolve()) in self.progress[section]

    def mark_done(self, section: str, path: Path):
        resolved = str(path.resolve())
        if resolved in self.progress[section]:
            return
        # Ensure section header exists
        if not self.progress[section]:
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(f"[{section}]\n")
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(resolved + "\n")
        self.progress[section].add(resolved)