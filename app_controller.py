import re
import threading
from tkinter import messagebox

from config import DEFAULT_SETTINGS, SETTINGS_FILE, HISTORY_FILE, PROFILES_FILE
from models import DownloadTask
from utils.file_utils import load_json, save_json, add_history
from utils.yt_dlp_builder import build_command
from services.info_service import InfoService
from services.video_downloader import VideoDownloader
from services.audio_downloader import AudioDownloader
from services.subtitle_downloader import SubtitleDownloader
from services.playlist_service import PlaylistService
from services.queue_service import QueueService
from services.setup_service import SetupService
from services.proxy_service import ProxyService


class AppController:
    def __init__(self, root):
        self.root = root
        self.settings = load_json(SETTINGS_FILE, DEFAULT_SETTINGS)
        self.history = load_json(HISTORY_FILE, [])
        self.profiles = load_json(PROFILES_FILE, {})
        self.active_proxy = ""
        self.info_service = InfoService()
        self.video_downloader = VideoDownloader()
        self.audio_downloader = AudioDownloader()
        self.subtitle_downloader = SubtitleDownloader()
        self.playlist_service = PlaylistService()
        self.setup_service = SetupService()
        self.proxy_service = ProxyService()
        self.gui = None
        self.queue_service = None

    def bind_gui(self, gui):
        self.gui = gui
        self.queue_service = QueueService(self)

    def ui(self, fn, *args, **kwargs):
        self.root.after(0, lambda: fn(*args, **kwargs))

    def save_settings(self):
        save_json(SETTINGS_FILE, self.settings)

    def log(self, text):
        self.ui(self.gui.append_log, text)

    def make_task_from_gui(self, url):
        return DownloadTask(
            url=url,
            format_name=self.gui.fmt_var.get(),
            quality=self.gui.qual_var.get(),
            output_dir=self.gui.folder_var.get(),
            filename_template=self.gui.fname_var.get() or "%(title)s.%(ext)s",
            subtitle_langs=self.settings.get("sub_langs", ["en"]),
            sub_all=self.settings.get("sub_all", False),
            sub_auto=self.settings.get("sub_auto", False),
            sub_format=self.settings.get("sub_format", "srt"),
            embed_thumbnail=self.gui.emb_thumb.get(),
            embed_subtitles=self.gui.emb_subs.get(),
            embed_metadata=self.settings.get("embed_metadata", True),
            sponsorblock=self.settings.get("sponsorblock", False),
            all_audio_langs=self.settings.get("all_audio_langs", False),
            proxy_url=self.active_proxy,
            player_clients=self.settings.get("player_clients", "android,web"),
        )

    def fetch_info_clicked(self):
        urls = self.gui.get_urls()
        if not urls:
            messagebox.showwarning("Fetch Info", "Enter a URL first.")
            return
        threading.Thread(target=self._fetch_info_worker, args=(urls[0],), daemon=True).start()

    def _fetch_info_worker(self, url):
        try:
            info = self.info_service.fetch_info(url, self.settings.get("player_clients", "android,web"), self.active_proxy)
            text = (
                f"{info.title}\n\n"
                f"Duration: {info.duration}\n"
                f"Uploader: {info.uploader}\n"
                f"Views: {info.view_count:,}\n"
                f"Likes: {info.like_count:,}\n"
                f"Upload: {info.upload_date}\n"
                f"Type: {'Playlist' if info.is_playlist else 'Video'}\n"
                f"Audio languages: {', '.join(info.audio_languages) or '—'}\n"
                f"Subtitle manual: {', '.join(info.subtitles.get('manual', [])) or '—'}\n"
                f"Subtitle auto: {', '.join(info.subtitles.get('auto', [])) or '—'}"
            )
            self.ui(self.gui.set_info_text, text)
        except Exception as e:
            self.ui(self.gui.set_info_text, f"Error: {e}")

    def start_download_clicked(self):
        urls = self.gui.get_urls()
        if not urls:
            messagebox.showwarning("Download", "Enter a URL first.")
            return
        threading.Thread(target=self._download_worker, args=(urls,), daemon=True).start()

    def _download_worker(self, urls):
        try:
            for i, url in enumerate(urls, 1):
                self.ui(self.gui.set_status, f"Downloading {i}/{len(urls)}…")
                task = self.make_task_from_gui(url)
                def on_line(line):
                    self.log(line)
                    m = re.search(r"\[download\]\s+([\d.]+)%", line)
                    if m:
                        self.ui(self.gui.prog_var.set, float(m.group(1)))
                code = self.video_downloader.download(task, self.settings, on_line)
                add_history(self.history, HISTORY_FILE, url, url, "✅ Done" if code == 0 else "❌ Failed")
            self.ui(self.gui.set_status, "✅ All downloads finished")
        except Exception as e:
            self.ui(self.gui.set_status, f"❌ Error: {e}")

    def add_to_queue_clicked(self):
        for url in self.gui.get_urls():
            self.gui.q_tree.insert("", "end", values=(url, "Pending", self.gui.fmt_var.get(), "0%"))

    def preview_command_clicked(self):
        urls = self.gui.get_urls()
        if not urls:
            messagebox.showwarning("Preview", "Enter a URL first.")
            return
        task = self.make_task_from_gui(urls[0])
        cmd = build_command(task, self.settings)
        messagebox.showinfo("Preview Command", " ".join(f'"{x}"' if " " in x else x for x in cmd))

    def load_playlist_clicked(self):
        url = self.gui.pl_url_var.get().strip()
        if not url:
            messagebox.showwarning("Playlist", "Enter playlist URL first.")
            return
        threading.Thread(target=self._load_playlist_worker, args=(url,), daemon=True).start()

    def _load_playlist_worker(self, url):
        entries = self.playlist_service.load_playlist(url, self.active_proxy)
        def apply():
            for item in self.gui.playlist_tree.get_children():
                self.gui.playlist_tree.delete(item)
            for i, entry in enumerate(entries, 1):
                self.gui.playlist_tree.insert("", "end", values=(i, entry.get("title", "Untitled"), entry.get("duration_string", "")))
        self.ui(apply)

    def check_tools_clicked(self):
        threading.Thread(target=self._check_tools_worker, daemon=True).start()

    def _check_tools_worker(self):
        results = self.setup_service.check_tools()
        self.ui(self.gui.set_tools_result, results)

    def update_queue_progress(self, url, progress):
        for item in self.gui.q_tree.get_children():
            values = self.gui.q_tree.item(item, "values")
            if values and values[0] == url:
                self.ui(self.gui.q_tree.set, item, "Progress", progress)
                self.ui(self.gui.q_tree.set, item, "Status", "Downloading")
                break

    def complete_queue_task(self, url, success):
        for item in self.gui.q_tree.get_children():
            values = self.gui.q_tree.item(item, "values")
            if values and values[0] == url:
                self.ui(self.gui.q_tree.set, item, "Status", "✅ Done" if success else "❌ Failed")
                if success:
                    self.ui(self.gui.q_tree.set, item, "Progress", "100%")
                break
        add_history(self.history, HISTORY_FILE, url, url, "✅ Done" if success else "❌ Failed")
