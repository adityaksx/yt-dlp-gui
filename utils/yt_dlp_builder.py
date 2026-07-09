import os
from config import QUALITY_MAP


def is_audio_only(fmt: str) -> bool:
    return any(x in fmt for x in ["MP3", "M4A", "FLAC", "Opus"])


def extractor_args_flag(player_clients: str):
    clients = (player_clients or "android,web").strip() or "android,web"
    return ["--extractor-args", f"youtube:player_client={clients};youtube:formats=missing_pot"]


def audio_format_string(height=None, all_audio_langs=False):
    vf = f"bestvideo[height={height}]" if height else "bestvideo"
    if all_audio_langs:
        return f"{vf}+mergeall[vcodec=none]/best[height={height}]" if height else f"{vf}+mergeall[vcodec=none]"
    return f"{vf}+bestaudio/best[height={height}]" if height else f"{vf}+bestaudio/best"


def video_only_format_string(height=None):
    return f"bestvideo[height={height}]" if height else "bestvideo"


def webm_format_string(height=None):
    if height:
        return f"bestvideo[ext=webm][height={height}]+bestaudio[ext=webm]/best[ext=webm][height={height}]"
    return "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]"


def subtitle_flags(task):
    if not task.embed_subtitles:
        return []
    flags = ["--write-subs"]
    if task.sub_auto:
        flags += ["--write-auto-subs"]
    lang_arg = "all" if task.sub_all else ",".join(task.subtitle_langs or ["en"])
    flags += ["--sub-langs", lang_arg, "--sub-format", task.sub_format]
    if not is_audio_only(task.format_name):
        flags += ["--embed-subs", "--convert-subs", task.sub_format]
    return flags


def metadata_flags(task, settings):
    flags = []
    if settings.get("embed_metadata", True) or task.embed_metadata:
        flags += ["--embed-metadata"]
    if task.embed_thumbnail:
        flags += ["--embed-thumbnail"]
    if settings.get("embed_chapters", True):
        flags += ["--embed-chapters"]
    if settings.get("meta_artist", True):
        flags += ["--parse-metadata", "%(uploader)s:%(meta_artist)s"]
    if settings.get("meta_year", True):
        flags += ["--parse-metadata", "%(upload_date>%Y)s:%(meta_year)s"]
    if settings.get("meta_album", True):
        flags += ["--parse-metadata", "%(playlist_title|)s:%(meta_album)s"]
    return flags


def sponsorblock_flags(task):
    return ["--sponsorblock-remove", "sponsor"] if task.sponsorblock else []


def build_command(task, settings):
    fmt = task.format_name
    quality = task.quality
    height = QUALITY_MAP.get(quality)
    cmd = ["yt-dlp"]
    cmd += extractor_args_flag(task.player_clients)

    if fmt in ("Best MP4", "WhatsApp MP4 480p", "WhatsApp MP4 720p", "WhatsApp MP4 1080p"):
        if fmt == "WhatsApp MP4 480p":
            height = 480
        elif fmt == "WhatsApp MP4 720p":
            height = 720
        elif fmt == "WhatsApp MP4 1080p":
            height = 1080
        cmd += ["-f", audio_format_string(height, task.all_audio_langs), "--merge-output-format", "mp4"]
    elif fmt.startswith("Best Quality"):
        cmd += ["-f", audio_format_string(height, task.all_audio_langs)]
    elif "MP3" in fmt:
        cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0"]
        if task.all_audio_langs:
            cmd += ["-f", "mergeall[vcodec=none]"]
    elif "M4A" in fmt:
        cmd += ["-x", "--audio-format", "m4a"]
        if task.all_audio_langs:
            cmd += ["-f", "mergeall[vcodec=none]"]
    elif "FLAC" in fmt:
        cmd += ["-x", "--audio-format", "flac"]
    elif "Opus" in fmt:
        cmd += ["-x", "--audio-format", "opus"]
    elif fmt == "Video Only":
        cmd += ["-f", video_only_format_string(height)]
    elif fmt == "WebM":
        cmd += ["-f", webm_format_string(height)]

    if task.all_audio_langs:
        cmd += ["--audio-multistreams"]

    cmd += metadata_flags(task, settings)
    cmd += sponsorblock_flags(task)
    cmd += subtitle_flags(task)

    cmd += ["-P", task.output_dir, "-o", task.filename_template]

    speed = settings.get("speed_limit", "0")
    if speed and speed != "0":
        cmd += ["-r", f"{speed}K"]

    cookie = settings.get("cookie_file", "")
    if cookie and os.path.exists(cookie):
        cmd += ["--cookies", cookie]

    if task.proxy_url:
        cmd += ["--proxy", task.proxy_url]

    cmd += ["--newline", "--no-warnings", task.url]
    return cmd
