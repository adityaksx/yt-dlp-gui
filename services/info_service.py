import json
import re
import subprocess
from models import MediaInfo
from utils.yt_dlp_builder import extractor_args_flag
from utils.validators import detect_link_type


class InfoService:
    def fetch_info(self, url: str, player_clients: str, proxy_url: str = "") -> MediaInfo:
        cmd = ["yt-dlp", "--dump-single-json", "--skip-download", "--no-warnings"]
        cmd += extractor_args_flag(player_clients)
        if proxy_url:
            cmd += ["--proxy", proxy_url]
        cmd.append(url)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        if result.returncode != 0 or not result.stdout.strip():
            raise RuntimeError((result.stderr or "Could not fetch info").strip())
        raw = json.loads(result.stdout)
        subtitles = self.fetch_subtitles_from_info(raw)
        audio_languages = sorted({f.get("language") for f in (raw.get("formats") or []) if f.get("language")})
        return MediaInfo(
            title=raw.get("title", ""),
            duration=raw.get("duration_string", ""),
            uploader=raw.get("uploader", ""),
            thumbnail=raw.get("thumbnail", ""),
            view_count=raw.get("view_count") or 0,
            like_count=raw.get("like_count") or 0,
            upload_date=raw.get("upload_date", ""),
            categories=raw.get("categories") or [],
            tags=raw.get("tags") or [],
            subtitles=subtitles,
            audio_languages=audio_languages,
            formats=raw.get("formats") or [],
            is_playlist=detect_link_type(url) == "playlist",
            needs_proxy=False,
        )

    def fetch_subtitles_from_info(self, raw: dict):
        lang_re = re.compile(r"^[a-zA-Z]{2,3}([_-][a-zA-Z0-9]+)*$")
        manual = sorted(k for k in (raw.get("subtitles") or {}).keys() if k != "live_chat" and lang_re.match(k))
        auto = sorted(k for k in (raw.get("automatic_captions") or {}).keys() if k != "live_chat" and lang_re.match(k))
        return {"manual": manual, "auto": auto}
