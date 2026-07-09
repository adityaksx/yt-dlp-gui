import shutil


class SetupService:
    def check(self):
        return {
            "yt-dlp": shutil.which("yt-dlp") is not None,
            "ffmpeg": shutil.which("ffmpeg") is not None,
            "python": shutil.which("python3") is not None,
        }

    def install_text(self):
        return (
            "Install / update commands\n\n"
            "Python package:\n"
            "python3 -m pip install -U yt-dlp pillow\n\n"
            "Fedora:\n"
            "sudo dnf install ffmpeg\n\n"
            "Ubuntu / Debian:\n"
            "sudo apt install ffmpeg\n\n"
            "Arch:\n"
            "sudo pacman -S ffmpeg\n\n"
            "Windows:\n"
            "winget install Gyan.FFmpeg\n"
        )
