import json

def load_comments(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
