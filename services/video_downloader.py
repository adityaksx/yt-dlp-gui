import subprocess
from utils.yt_dlp_builder import build_command


class VideoDownloader:
    def run(self, task, settings, line_callback=None):
        cmd = build_command(task, settings)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
        for line in proc.stdout:
            line = line.rstrip()
            if line_callback:
                line_callback(line)
        proc.wait()
        return proc.returncode, cmd
