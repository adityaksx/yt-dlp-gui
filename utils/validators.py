
def detect_link_type(url: str) -> str:
    u = (url or "").lower().strip()
    if any(k in u for k in ["playlist?list=", "/playlist/", "/channel/", "/c/", "/@"]):
        return "playlist"
    return "video"


def split_urls(text: str):
    return [line.strip() for line in (text or "").splitlines() if line.strip()]
