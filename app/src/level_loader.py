"""Level loading and management."""
import os
import sys

LEVEL_DIR = os.path.join(os.path.dirname(__file__), "..", "levels")

def list_level_files():
    if not os.path.isdir(LEVEL_DIR):
        return []
    files = [f for f in os.listdir(LEVEL_DIR) if f.lower().endswith(".txt")]
    files.sort()
    return files

def load_level_file(filename):
    path = os.path.join(LEVEL_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]
    # Validate rectangular
    if not lines:
        raise ValueError("Level file is empty.")
    width = len(lines[0])
    for i, line in enumerate(lines):
        if len(line) != width:
            raise ValueError(f"Row {i} length {len(line)} != {width} (level must be rectangular)")
    return lines

def get_initial_level():
    """Get initial level from LEVEL env var or return None for default behavior"""
    level_env = os.environ.get('LEVEL')
    if level_env:
        files = list_level_files()
        cand = level_env + ".txt"
        if cand in files:
            return level_env
        else:
            print(f"Warning: Level '{level_env}' not found. Available levels:")
            for f in files:
                print(f"  - {os.path.splitext(f)[0]}")
            print("Falling back to default level selection.")
    return None

def choose_level_interactive():
    files = list_level_files()
    if not files:
        print("No level files found in ./levels.\n"
              "Create at least one .txt file with your map. "
              "Example filenames: classic_28x31.txt, demo_64x64.txt")
        sys.exit(1)

    while True:
        print("\nAvailable levels:")
        for f in files:
            print("  -", os.path.splitext(f)[0])
        inp = input("\nEnter level name (without .txt). Press ENTER to load first: ").strip()
        if inp == "":
            chosen = files[0]
            print(f"Loading: {chosen}")
            return load_level_file(chosen), os.path.splitext(chosen)[0]
        cand = inp + ".txt"
        if cand in files:
            print(f"Loading: {cand}")
            return load_level_file(cand), inp
        else:
            print(f"'{inp}' not found.")