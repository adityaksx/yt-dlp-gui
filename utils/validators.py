
def detect_link_type(url: str) -> str:
    url = (url or "").strip().lower()
    if not url:
        return "unknown"
    if any(key in url for key in ["playlist?list=", "/playlist/", "/channel/", "/c/", "/@"]):
        return "playlist"
    return "video"


def is_probably_url(text: str) -> bool:
    return text.startswith("http://") or text.startswith("https://")
