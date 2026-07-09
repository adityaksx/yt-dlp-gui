import json
import subprocess


class PlaylistService:
    def load(self, url: str, proxy: str = ""):
        cmd = ["yt-dlp", "--flat-playlist", "--dump-json", "--no-warnings"]
        if proxy:
            cmd += ["--proxy", proxy]
        cmd.append(url)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
        items = []
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except Exception:
                pass
        proc.wait()
        return items
