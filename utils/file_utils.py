import json
import os
import shutil
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
            pass
    return default.copy() if isinstance(default, dict) else list(default)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def add_history(history, path, url, title, status):
    history.append({
        "url": url,
        "title": title,
        "status": status,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    history[:] = history[-300:]
    save_json(path, history)


def which(name):
    return shutil.which(name)


def safe_filename(name):
    bad = '<>:"/\\|?*'
    for ch in bad:
        name = name.replace(ch, "_")
    return name.strip() or "output"
