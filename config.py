import os

SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".ytdlp_pro_settings.json")
HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".ytdlp_pro_history.json")
PROFILES_FILE = os.path.join(os.path.expanduser("~"), ".ytdlp_pro_profiles.json")

DEFAULT_PLAYER_CLIENTS = "android,web"

DEFAULT_SETTINGS = {
    "theme": "dark",
    "save_folder": os.path.expanduser("~/Downloads"),
    "format": "Best MP4",
    "quality": "Best",
    "filename_template": "%(title)s.%(ext)s",
    "fragments": "5",
    "concurrent_dl": "2",
    "embed_thumbnail": True,
    "embed_subs": False,
    "sub_langs": ["en"],
    "sub_all": False,
    "sub_auto": False,
    "sub_format": "srt",
    "all_audio_langs": False,
    "player_clients": DEFAULT_PLAYER_CLIENTS,
    "cookie_file": "",
    "speed_limit": "0",
    "embed_metadata": True,
    "embed_chapters": True,
    "meta_artist": True,
    "meta_year": True,
    "meta_album": True,
    "playlist_folder": True,
    "sponsorblock": False,
    "clipboard_watch": False,
}

THEMES = {
    "dark": {
        "bg": "#1e1e2e", "surface": "#313244", "surface2": "#45475a",
        "text": "#cdd6f4", "sub": "#a6adc8", "blue": "#89b4fa", "green": "#a6e3a1",
        "red": "#f38ba8", "yellow": "#f9e2af", "mauve": "#cba6f7", "teal": "#94e2d5",
        "peach": "#fab387",
    },
    "light": {
        "bg": "#eff1f5", "surface": "#e6e9ef", "surface2": "#dce0e8",
        "text": "#4c4f69", "sub": "#6c6f85", "blue": "#1e66f5", "green": "#40a02b",
        "red": "#d20f39", "yellow": "#df8e1d", "mauve": "#8839ef", "teal": "#179299",
        "peach": "#fe640b",
    },
}

QUALITY_MAP = {
    "Best": None,
    "4K (2160p)": 2160,
    "1440p": 1440,
    "1080p": 1080,
    "720p": 720,
    "480p": 480,
    "360p": 360,
    "240p": 240,
}

FORMATS = [
    "Best MP4",
    "Best Quality (MKV)",
    "Audio Only (MP3)",
    "Audio Only (M4A)",
    "Audio Only (FLAC)",
    "Audio Only (Opus)",
    "Video Only",
    "WebM",
    "WhatsApp MP4 480p",
    "WhatsApp MP4 720p",
    "WhatsApp MP4 1080p",
]
