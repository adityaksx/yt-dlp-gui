from utils.file_utils import which


class SetupService:
    def check_tools(self):
        return {
            "yt-dlp": which("yt-dlp") is not None,
            "ffmpeg": which("ffmpeg") is not None,
            "python-pillow": which("python3") is not None,
        }
