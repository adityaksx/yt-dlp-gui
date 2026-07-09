from datetime import datetime


class Logger:
    def __init__(self, callback=None):
        self.callback = callback

    def write(self, level, message):
        line = f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] {message}"
        if self.callback:
            self.callback(line)
        return line

    def info(self, msg):
        return self.write("INFO", msg)

    def warn(self, msg):
        return self.write("WARN", msg)

    def error(self, msg):
        return self.write("ERROR", msg)
