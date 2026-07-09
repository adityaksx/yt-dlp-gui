import json
import subprocess


class PlaylistService:
    def load_playlist(self, url: str, proxy_url: str = ""):
        cmd = ["yt-dlp", "--flat-playlist", "--dump-json", "--no-warnings"]
        if proxy_url:
            cmd += ["--proxy", proxy_url]
        cmd.append(url)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace")
        entries = []
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except Exception:
                pass
        proc.wait()
        return entries
