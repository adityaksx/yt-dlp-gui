from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class DownloadTask:
    url: str
    format_name: str
    quality: str
    output_dir: str
    filename_template: str
    embed_thumbnail: bool = False
    embed_subtitles: bool = False
    embed_metadata: bool = True
    subtitle_langs: List[str] = field(default_factory=lambda: ["en"])
    subtitle_format: str = "srt"
    subtitle_auto: bool = True
    audio_langs: List[str] = field(default_factory=list)
    all_audio_langs: bool = False
    sponsorblock: bool = False
    player_clients: str = "android,web"
    proxy: str = ""
    source_type: str = "video"
    playlist_items: Optional[List[int]] = None

@dataclass
class MediaInfo:
    title: str = ""
    duration: str = ""
    uploader: str = ""
    thumbnail: str = ""
    upload_date: str = ""
    view_count: int = 0
    like_count: int = 0
    webpage_url: str = ""
    source_type: str = "video"
    subtitles_manual: List[str] = field(default_factory=list)
    subtitles_auto: List[str] = field(default_factory=list)
    audio_languages: List[str] = field(default_factory=list)
    formats: List[Dict[str, Any]] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)

@dataclass
class QueueItem:
    task: DownloadTask
    status: str = "Pending"
    progress: str = "0%"
    speed: str = ""
