import json
import re
import subprocess
from models import MediaInfo
from utils.validators import detect_link_type
from utils.yt_dlp_builder import build_extractors


class InfoService:
    def fetch(self, url: str, player_clients: str, proxy: str = "") -> MediaInfo:
        cmd = ["yt-dlp", "--dump-single-json", "--skip-download", "--no-warnings"]
        cmd += build_extractors(player_clients)
        if proxy:
            cmd += ["--proxy", proxy]
        cmd.append(url)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        if result.returncode != 0 or not result.stdout.strip():
            err = (result.stderr or "Failed to fetch info").strip()
            raise RuntimeError(err)
        data = json.loads(result.stdout)
        lang_re = re.compile(r"^[a-zA-Z]{2,3}([_-][a-zA-Z0-9]+)*$")
        subs = sorted(k for k in (data.get("subtitles") or {}).keys() if k != "live_chat" and lang_re.match(k))
        auto = sorted(k for k in (data.get("automatic_captions") or {}).keys() if k != "live_chat" and lang_re.match(k))
        audio_langs = sorted({f.get("language") for f in (data.get("formats") or []) if f.get("language")})
        return MediaInfo(
            title=data.get("title", ""),
            duration=data.get("duration_string", ""),
            uploader=data.get("uploader", ""),
            thumbnail=data.get("thumbnail", ""),
            upload_date=data.get("upload_date", ""),
            view_count=data.get("view_count") or 0,
            like_count=data.get("like_count") or 0,
            webpage_url=data.get("webpage_url", url),
            source_type=detect_link_type(url),
            subtitles_manual=subs,
            subtitles_auto=auto,
            audio_languages=audio_langs,
            formats=data.get("formats") or [],
            raw=data,
        )
