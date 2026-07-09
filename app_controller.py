import io
import re
from tkinter import messagebox

from config import DEFAULT_SETTINGS, SETTINGS_FILE, HISTORY_FILE
from models import DownloadTask
from utils.file_utils import load_json, save_json, append_history
from utils.log_utils import Logger
from utils.thread_utils import UIThread, start_thread
from utils.validators import split_urls, detect_link_type
from utils.yt_dlp_builder import build_command
from services.info_service import InfoService
from services.playlist_service import PlaylistService
from services.proxy_service import ProxyService
from services.setup_service import SetupService
from services.thumbnail_metadata import ThumbnailMetadataService
from services.video_downloader import VideoDownloader
from services.audio_downloader import AudioDownloader
from services.subtitle_downloader import SubtitleDownloader
from services.combiner_service import CombinerService
from services.queue_service import QueueService

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class AppController:
    def __init__(self, root):
        self.root = root
        self.ui = UIThread(root)
        self.settings = load_json(SETTINGS_FILE, DEFAULT_SETTINGS)
        self.logger = Logger(callback=self._emit_log)
        self.info_service = InfoService()
        self.playlist_service = PlaylistService()
        self.proxy_service = ProxyService()
        self.setup_service = SetupService()
        self.thumb_service = ThumbnailMetadataService()
        self.video_downloader = VideoDownloader()
        self.audio_downloader = AudioDownloader()
        self.subtitle_downloader = SubtitleDownloader()
        self.combiner_service = CombinerService()
        self.gui = None
        self.queue_service = None
        self.current_info = None
        self.current_process_note = ""

    def bind_gui(self, gui):
        self.gui = gui
        self.queue_service = QueueService(self)
        self.refresh_proxy_badge()

    def _emit_log(self, line):
        if self.gui:
            self.ui.call(self.gui.append_log, line)

    def log(self, line):
        self.logger.info(line)

    def save_settings(self):
        save_json(SETTINGS_FILE, self.settings)

    def refresh_proxy_badge(self):
        if self.gui:
            proxy = self.proxy_service.get_proxy(self.settings)
            self.ui.call(self.gui.set_proxy_text, self.proxy_service.label(proxy))

    def gather_task(self, url, source_type=None, playlist_items=None):
        return DownloadTask(
            url=url,
            format_name=self.gui.fmt_var.get(),
            quality=self.gui.qual_var.get(),
            output_dir=self.gui.folder_var.get(),
            filename_template=self.gui.fname_var.get(),
            embed_thumbnail=self.gui.embed_thumb_var.get(),
            embed_subtitles=self.gui.embed_subs_var.get(),
            embed_metadata=self.gui.embed_meta_var.get(),
            subtitle_langs=self.gui.get_selected_subtitle_langs(),
            subtitle_format=self.gui.sub_fmt_var.get(),
            subtitle_auto=self.gui.sub_auto_var.get(),
            audio_langs=self.gui.get_selected_audio_langs(),
            all_audio_langs=self.gui.all_audio_var.get(),
            sponsorblock=self.gui.sponsor_var.get(),
            player_clients=self.settings.get("player_clients", "android,web"),
            proxy=self.proxy_service.get_proxy(self.settings),
            source_type=source_type or detect_link_type(url),
            playlist_items=playlist_items,
        )

    def pick_downloader(self, task):
        if "Audio Only" in task.format_name:
            return self.audio_downloader
        if task.embed_subtitles and task.format_name == "Video Only":
            return self.subtitle_downloader
        return self.video_downloader

    def fetch_info(self):
        urls = split_urls(self.gui.url_text.get("1.0", "end"))
        if not urls:
            messagebox.showwarning("Fetch Info", "Enter a URL first.")
            return
        start_thread(self._fetch_info_worker, urls[0])

    def _fetch_info_worker(self, url):
        try:
            self.ui.call(self.gui.set_status, "Fetching info…")
            info = self.info_service.fetch(url, self.settings.get("player_clients", "android,web"), self.proxy_service.get_proxy(self.settings))
            self.current_info = info
            self.ui.call(self.gui.update_info_box, info)
            self.ui.call(self.gui.set_detected_languages, info.audio_languages, info.subtitles_manual, info.subtitles_auto)
            self.ui.call(self.gui.set_status, "Info loaded")
            if info.thumbnail and HAS_PIL:
                data = self.thumb_service.fetch_thumbnail_bytes(info.thumbnail)
                if data:
                    img = Image.open(io.BytesIO(data)).resize((300, 170), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.ui.call(self.gui.set_thumbnail, photo)
        except Exception as e:
            self.ui.call(self.gui.set_status, f"Error: {e}")
            self.logger.error(str(e))

    def _handle_download_failure(self, url, error_lines):
        text = "\n".join(error_lines)
        if "Requested format is not available" in text:
            self.logger.warn("Requested format failed. Fetching available formats...")
            formats = self.info_service.list_formats(url, self.settings.get("player_clients", "android,web"), self.proxy_service.get_proxy(self.settings))
            self.ui.call(self.gui.show_format_fallback, formats)

    def download_now(self):
        urls = split_urls(self.gui.url_text.get("1.0", "end"))
        if not urls:
            messagebox.showwarning("Download", "Enter a URL first.")
            return
        start_thread(self._download_now_worker, urls)

    def _download_now_worker(self, urls):
        total = len(urls)
        for i, url in enumerate(urls, 1):
            task = self.gather_task(url)
            self.ui.call(self.gui.set_status, f"Downloading {i}/{total}")
            errors = []
            def on_line(line):
                self.logger.info(line)
                if "ERROR:" in line:
                    errors.append(line)
                m = re.search(r"\[download\]\s+([\d.]+)%.*?at\s+([^\s]+)", line)
                if m:
                    self.ui.call(self.gui.set_progress, float(m.group(1)))
                    self.ui.call(self.gui.set_speed, m.group(2))
            code, cmd = self.pick_downloader(task).run(task, self.settings, on_line)
            self.current_process_note = " ".join(cmd)
            if code != 0:
                self._handle_download_failure(url, errors)
            append_history(HISTORY_FILE, url, getattr(self.current_info, 'title', url), "Done" if code == 0 else "Failed")
        self.ui.call(self.gui.set_status, "Download complete")

    def add_queue(self):
        urls = split_urls(self.gui.url_text.get("1.0", "end"))
        if not urls:
            messagebox.showwarning("Queue", "Enter at least one URL.")
            return
        tasks = []
        for url in urls:
            task = self.gather_task(url)
            tasks.append(task)
            self.ui.call(self.gui.queue_add_row, task.url, "Pending", task.format_name, "0%", "")
        self.queue_service.add_and_start(tasks)
        self.ui.call(self.gui.set_status, f"Added {len(tasks)} item(s) to queue")

    def queue_status(self, url, status, progress, speed=""):
        self.ui.call(self.gui.queue_update_row, url, status, progress, speed)

    def queue_done(self, url, success):
        self.ui.call(self.gui.queue_update_row, url, "Done" if success else "Failed", "100%" if success else "0%", "")
        append_history(HISTORY_FILE, url, url, "Done" if success else "Failed")

    def preview_command(self):
        urls = split_urls(self.gui.url_text.get("1.0", "end"))
        if not urls:
            messagebox.showwarning("Preview", "Enter a URL first.")
            return
        task = self.gather_task(urls[0])
        cmd = build_command(task, self.settings)
        self.current_process_note = " ".join(cmd)
        messagebox.showinfo("Preview Command", self.current_process_note)

    def load_playlist(self):
        url = self.gui.playlist_url_var.get().strip()
        if not url:
            messagebox.showwarning("Playlist", "Enter playlist URL first.")
            return
        start_thread(self._load_playlist_worker, url)

    def _load_playlist_worker(self, url):
        try:
            self.ui.call(self.gui.set_playlist_status, "Loading playlist…")
            items = self.playlist_service.load(url, self.proxy_service.get_proxy(self.settings))
            self.ui.call(self.gui.populate_playlist, items)
            self.ui.call(self.gui.set_playlist_status, f"Loaded {len(items)} items")
        except Exception as e:
            self.ui.call(self.gui.set_playlist_status, f"Error: {e}")
            self.logger.error(str(e))

    def download_playlist_selected(self):
        url = self.gui.playlist_url_var.get().strip()
        selected = self.gui.get_selected_playlist_indices()
        if not url or not selected:
            messagebox.showwarning("Playlist", "Load a playlist and select items.")
            return
        task = self.gather_task(url, source_type="playlist", playlist_items=selected)
        self.ui.call(self.gui.queue_add_row, task.url, "Pending", task.format_name, f"Items: {len(selected)}", "")
        self.queue_service.add_and_start([task])

    def apply_settings(self):
        self.settings["save_folder"] = self.gui.settings_folder_var.get().strip() or self.settings["save_folder"]
        self.settings["filename_template"] = self.gui.settings_name_var.get().strip() or self.settings["filename_template"]
        self.settings["format"] = self.gui.settings_format_var.get()
        self.settings["quality"] = self.gui.settings_quality_var.get()
        self.settings["proxy"] = self.gui.settings_proxy_var.get().strip()
        self.settings["player_clients"] = self.gui.settings_player_clients_var.get().strip()
        self.settings["concurrent_downloads"] = int(self.gui.settings_concurrent_var.get())
        self.settings["prefer_tor"] = self.gui.settings_tor_var.get()
        self.settings["speed_limit_kbps"] = int(self.gui.settings_speed_var.get() or 0)
        self.save_settings()
        self.queue_service.reconfigure()
        self.refresh_proxy_badge()
        self.ui.call(self.gui.set_status, "Settings saved")

    def check_tools(self):
        results = self.setup_service.check()
        self.ui.call(self.gui.show_setup, results, self.setup_service.install_text())
