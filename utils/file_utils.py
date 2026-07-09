import json
import os
from datetime import datetime


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(default, dict):
                merged = default.copy()
                merged.update(data)
                return merged
            return data
        except Exception:
            return default.copy() if isinstance(default, dict) else list(default)
    return default.copy() if isinstance(default, dict) else list(default)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def append_history(path, url, title, status):
    history = load_json(path, [])
    history.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": url,
        "title": title,
        "status": status,
    })
    history = history[-300:]
    save_json(path, history)
