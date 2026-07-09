from config import QUALITY_MAP


def build_extractors(player_clients: str):
    clients = (player_clients or "android,web").strip() or "android,web"
    return ["--extractor-args", f"youtube:player_client={clients};youtube:formats=missing_pot"]


def is_audio_only(fmt: str):
    return "Audio Only" in fmt


def quality_height(label: str):
    return QUALITY_MAP.get(label)


def build_format_selector(fmt: str, quality: str, all_audio_langs: bool = False):
    h = quality_height(quality)
    if fmt == "Best MP4":
        return f"bestvideo[height={h}]+bestaudio/best[height={h}]" if h else "bestvideo+bestaudio/best"
    if fmt == "Best Quality (MKV)":
        return f"bestvideo[height={h}]+bestaudio/best[height={h}]" if h else "bestvideo+bestaudio/best"
    if fmt == "Video Only":
        return f"bestvideo[height={h}]" if h else "bestvideo"
    if fmt == "WebM":
        return f"bestvideo[ext=webm][height={h}]+bestaudio[ext=webm]/best[ext=webm][height={h}]" if h else "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]"
    if fmt == "WhatsApp MP4 480p":
        return "bestvideo[height<=480]+bestaudio/best[height<=480]"
    if fmt == "WhatsApp MP4 720p":
        return "bestvideo[height<=720]+bestaudio/best[height<=720]"
    if fmt == "WhatsApp MP4 1080p":
        return "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
    if all_audio_langs:
        return "mergeall[vcodec=none]"
    return "bestaudio/best"


def build_command(task, settings):
    cmd = ["yt-dlp"]
    cmd += build_extractors(task.player_clients)
    cmd += ["--newline", "--no-warnings"]
    if task.proxy:
        cmd += ["--proxy", task.proxy]
    fmt = task.format_name
    selector = build_format_selector(fmt, task.quality, task.all_audio_langs)
    if "Audio Only (MP3)" == fmt:
        cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0"]
    elif "Audio Only (M4A)" == fmt:
        cmd += ["-x", "--audio-format", "m4a"]
    elif "Audio Only (FLAC)" == fmt:
        cmd += ["-x", "--audio-format", "flac"]
    elif "Audio Only (Opus)" == fmt:
        cmd += ["-x", "--audio-format", "opus"]
    else:
        cmd += ["-f", selector]
    if fmt.startswith("WhatsApp") or fmt == "Best MP4":
        cmd += ["--merge-output-format", "mp4"]
    if task.embed_thumbnail:
        cmd += ["--embed-thumbnail"]
    if task.embed_metadata:
        cmd += ["--embed-metadata", "--embed-chapters"]
    if task.embed_subtitles:
        cmd += ["--write-subs", "--sub-format", task.subtitle_format]
        if task.subtitle_auto:
            cmd += ["--write-auto-subs"]
        cmd += ["--sub-langs", "all" if not task.subtitle_langs else ",".join(task.subtitle_langs)]
        if not is_audio_only(fmt):
            cmd += ["--embed-subs", "--convert-subs", task.subtitle_format]
    if task.all_audio_langs:
        cmd += ["--audio-multistreams"]
    if task.sponsorblock:
        cmd += ["--sponsorblock-remove", "sponsor"]
    speed = int(settings.get("speed_limit_kbps", 0) or 0)
    if speed > 0:
        cmd += ["-r", f"{speed}K"]
    cmd += ["-P", task.output_dir, "-o", task.filename_template]
    if task.playlist_items:
        cmd += ["--playlist-items", ",".join(str(x) for x in task.playlist_items)]
    cmd.append(task.url)
    return cmd
