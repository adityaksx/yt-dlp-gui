import re
from concurrent.futures import ThreadPoolExecutor


class QueueService:
    def __init__(self, controller):
        self.controller = controller
        self.executor = ThreadPoolExecutor(max_workers=int(controller.settings.get("concurrent_downloads", 2) or 2))
        self.futures = []
        self.paused = False

    def reconfigure(self):
        self.executor.shutdown(wait=False, cancel_futures=False)
        self.executor = ThreadPoolExecutor(max_workers=int(self.controller.settings.get("concurrent_downloads", 2) or 2))

    def add_and_start(self, tasks):
        for task in tasks:
            self.futures.append(self.executor.submit(self._run_task, task))

    def _run_task(self, task):
        self.controller.queue_status(task.url, "Downloading", "0%")
        def on_line(line):
            self.controller.log(line)
            m = re.search(r"\[download\]\s+([\d.]+)%.*?at\s+([^\s]+)", line)
            if m:
                self.controller.queue_status(task.url, "Downloading", f"{m.group(1)}%", m.group(2))
        code, _ = self.controller.pick_downloader(task).run(task, self.controller.settings, on_line)
        self.controller.queue_done(task.url, code == 0)
