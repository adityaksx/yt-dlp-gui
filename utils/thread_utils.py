import threading


class UIThread:
    def __init__(self, root):
        self.root = root

    def call(self, fn, *args, **kwargs):
        self.root.after(0, lambda: fn(*args, **kwargs))


def start_thread(target, *args, daemon=True, **kwargs):
    t = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=daemon)
    t.start()
    return t
