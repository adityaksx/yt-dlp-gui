import os

APP_NAME = "yt-dlp Modern GUI"
APP_VERSION = "3.0"

BASE_DIR = os.path.expanduser("~")
SETTINGS_FILE = os.path.join(BASE_DIR, ".ytdlp_modern_settings.json")
HISTORY_FILE = os.path.join(BASE_DIR, ".ytdlp_modern_history.json")

DEFAULT_PLAYER_CLIENTS = "android,web"
DEFAULT_PROXY = ""
DEFAULT_OUTPUT = os.path.expanduser("~/Downloads")

FORMATS = [
    "Best MP4",
    "Best Quality (MKV)",
    "Video Only",
    "WebM",
    "Audio Only (MP3)",
    "Audio Only (M4A)",
    "Audio Only (FLAC)",
    "Audio Only (Opus)",
    "WhatsApp MP4 480p",
    "WhatsApp MP4 720p",
    "WhatsApp MP4 1080p",
]

QUALITY_MAP = {
    "Best": None,
    "2160p": 2160,
    "1440p": 1440,
    "1080p": 1080,
    "720p": 720,
    "480p": 480,
    "360p": 360,
    "240p": 240,
}

SUBTITLE_FORMATS = ["srt", "vtt", "ass"]
THEME_COLORS = {
    "bg": "#0f172a",
    "surface": "#111827",
    "surface2": "#1f2937",
    "surface3": "#334155",
    "card": "#111827",
    "text": "#e5e7eb",
    "sub": "#94a3b8",
    "muted": "#64748b",
    "blue": "#38bdf8",
    "green": "#22c55e",
    "amber": "#f59e0b",
    "red": "#ef4444",
    "purple": "#a78bfa",
    "border": "#243041",
}

DEFAULT_SETTINGS = {
    "save_folder": DEFAULT_OUTPUT,
    "filename_template": "%(title)s.%(ext)s",
    "format": "Best MP4",
    "quality": "Best",
    "player_clients": DEFAULT_PLAYER_CLIENTS,
    "proxy": DEFAULT_PROXY,
    "embed_thumbnail": True,
    "embed_subtitles": False,
    "embed_metadata": True,
    "subtitle_format": "srt",
    "subtitle_langs": ["en"],
    "subtitle_auto": True,
    "audio_langs": [],
    "all_audio_langs": False,
    "sponsorblock": False,
    "concurrent_downloads": 2,
    "speed_limit_kbps": 0,
    "prefer_tor": False,
}
