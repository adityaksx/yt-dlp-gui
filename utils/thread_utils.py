import threading
from functools import wraps


def run_in_thread(daemon: bool = True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=daemon)
            thread.start()
            return thread
        return wrapper
    return decorator


class UIThreadExecutor:
    def __init__(self, root):
        self.root = root

    def call(self, fn, *args, **kwargs):
        self.root.after(0, lambda: fn(*args, **kwargs))


class WorkerPool:
    def __init__(self, max_workers: int = 2):
        self.max_workers = max(1, int(max_workers))
        self.semaphore = threading.Semaphore(self.max_workers)
        self.active_threads = []

    def submit(self, func, *args, **kwargs):
        def runner():
            with self.semaphore:
                func(*args, **kwargs)

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()
        self.active_threads.append(thread)
        self.active_threads = [t for t in self.active_threads if t.is_alive()]
        return thread

    def wait_all(self):
        for thread in list(self.active_threads):
            thread.join()
