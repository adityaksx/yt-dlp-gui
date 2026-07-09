import urllib.request


class ThumbnailMetadataService:
    def fetch_thumbnail_bytes(self, url: str):
        if not url:
            return None
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.read()
