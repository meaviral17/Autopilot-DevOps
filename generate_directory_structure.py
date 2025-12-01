import os
import json

IGNORE_DIRS = {'.git', '__pycache__', 'venv', 'node_modules', 'cache', 'images','.vscode','drive-mad','generate_directory_structure.py'}

IGNORE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.exe', '.dll', '.gitignore'}
ALWAYS_TEXT_FILES = {'.md'}

def read_file(file_path):
    """Try reading a file with UTF-8 first, then UTF-16 as fallback."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='utf-16') as f:
                return f.read()
        except Exception:
            return "<could not read file>"

def read_directory(path):
    result = {}
    for entry in os.scandir(path):
        if entry.is_dir():
            if entry.name in IGNORE_DIRS:
                continue
            result[entry.name] = read_directory(entry.path)
        elif entry.is_file():
            if any(entry.name.lower().endswith(ext) for ext in IGNORE_EXTENSIONS):
                continue
            _, ext = os.path.splitext(entry.name)
            if ext.lower() in ALWAYS_TEXT_FILES or True:
                result[entry.name] = read_file(entry.path)
    return result

root_dir = '.'  # current directory

directory_structure = read_directory(root_dir)

with open('directory_structure.json', 'w', encoding='utf-8') as f:
    json.dump(directory_structure, f, ensure_ascii=False, indent=4)

print("Directory structure saved to 'directory_structure.json'")