from datetime import datetime
from pathlib import Path


class Logger:
    def __init__(self, log_file: str | None = None, callback=None):
        self.log_file = Path(log_file) if log_file else None
        self.callback = callback

    def _write(self, level: str, message: str):
        line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}"
        if self.callback:
            self.callback(line)
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with self.log_file.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
        return line

    def info(self, message: str):
        return self._write("INFO", message)

    def warning(self, message: str):
        return self._write("WARN", message)

    def error(self, message: str):
        return self._write("ERROR", message)

    def debug(self, message: str):
        return self._write("DEBUG", message)
