# core/file_manager.py
import os

def read_file(filepath):
    """Reads content from a file."""
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()

def write_file(filepath, content):
    """Writes content to a file."""
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(content)