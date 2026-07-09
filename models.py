from dataclasses import dataclass, field
from typing import List, Optional, Literal, Dict, Any

TaskType = Literal["video", "audio", "subtitle", "thumbnail", "playlist", "combined", "info"]

@dataclass
class DownloadTask:
    url: str
    task_type: TaskType = "video"
    format_name: str = "Best MP4"
    quality: str = "Best"
    output_dir: str = ""
    filename_template: str = "%(title)s.%(ext)s"
    subtitle_langs: List[str] = field(default_factory=lambda: ["en"])
    sub_all: bool = False
    sub_auto: bool = False
    sub_format: str = "srt"
    audio_langs: List[str] = field(default_factory=list)
    embed_thumbnail: bool = False
    embed_subtitles: bool = False
    embed_metadata: bool = True
    sponsorblock: bool = False
    all_audio_langs: bool = False
    proxy_url: str = ""
    playlist_items: Optional[List[int]] = None
    player_clients: str = "android,web"

@dataclass
class MediaInfo:
    title: str = ""
    duration: str = ""
    uploader: str = ""
    thumbnail: str = ""
    view_count: int = 0
    like_count: int = 0
    upload_date: str = ""
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    subtitles: Dict[str, List[str]] = field(default_factory=dict)
    audio_languages: List[str] = field(default_factory=list)
    formats: List[Dict[str, Any]] = field(default_factory=list)
    is_playlist: bool = False
    needs_proxy: bool = False
