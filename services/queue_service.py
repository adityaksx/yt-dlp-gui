import re
import threading
from services.video_downloader import VideoDownloader


class QueueService:
    def __init__(self, controller):
        self.controller = controller
        self.max_concurrent = int(controller.settings.get("concurrent_dl", "2") or 2)
        self.semaphore = threading.Semaphore(self.max_concurrent)
        self.running = False
        self.downloader = VideoDownloader()

    def update_concurrency(self, value: int):
        self.max_concurrent = max(1, int(value))
        self.semaphore = threading.Semaphore(self.max_concurrent)
        self.controller.settings["concurrent_dl"] = str(self.max_concurrent)
        self.controller.save_settings()

    def run_tasks(self, tasks):
        if self.running:
            return
        self.running = True
        threads = [threading.Thread(target=self._run_one, args=(task,), daemon=True) for task in tasks]
        for th in threads:
            th.start()
        for th in threads:
            th.join()
        self.running = False

    def _run_one(self, task):
        with self.semaphore:
            def on_line(line):
                self.controller.log(line)
                match = re.search(r"\[download\]\s+([\d.]+)%", line)
                if match:
                    self.controller.update_queue_progress(task.url, f"{match.group(1)}%")
            code = self.downloader.download(task, self.controller.settings, on_line)
            self.controller.complete_queue_task(task.url, code == 0)
