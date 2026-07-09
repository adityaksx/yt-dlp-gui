import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from config import THEMES, FORMATS, QUALITY_MAP


class AppGUI:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.C = THEMES.get(controller.settings.get("theme", "dark"), THEMES["dark"])
        self.root.configure(bg=self.C["bg"])
        self.root.title("yt-dlp Pro Modular")
        self.root.geometry("1120x760")
        self._setup_styles()
        self._build_ui()

    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        c = self.C
        s.configure(".", background=c["bg"], foreground=c["text"], font=("Segoe UI", 10))
        s.configure("TFrame", background=c["bg"])
        s.configure("TLabel", background=c["bg"], foreground=c["text"])
        s.configure("TLabelframe", background=c["bg"], bordercolor=c["surface2"])
        s.configure("TLabelframe.Label", background=c["bg"], foreground=c["blue"], font=("Segoe UI", 10, "bold"))
        s.configure("TButton", background=c["blue"], foreground=c["bg"], borderwidth=0)
        s.configure("Green.TButton", background=c["green"], foreground=c["bg"])
        s.configure("Red.TButton", background=c["red"], foreground=c["bg"])
        s.configure("TNotebook", background=c["bg"], borderwidth=0)
        s.configure("TNotebook.Tab", background=c["surface"], foreground=c["sub"], padding=[14, 7])
        s.configure("Treeview", background=c["surface"], foreground=c["text"], fieldbackground=c["surface"], rowheight=26)
        s.configure("Treeview.Heading", background=c["surface2"], foreground=c["blue"], font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        bar = tk.Frame(self.root, bg=self.C["surface"], height=48)
        bar.pack(fill="x")
        tk.Label(bar, text="▶ yt-dlp Pro Modular", bg=self.C["surface"], fg=self.C["blue"], font=("Segoe UI", 14, "bold")).pack(side="left", padx=14, pady=8)
        self.tool_badge = tk.Label(bar, text="⏳ Checking tools…", bg=self.C["surface"], fg=self.C["sub"], font=("Segoe UI", 9))
        self.tool_badge.pack(side="left", padx=10)
        self.proxy_badge = tk.Label(bar, text="⚪ No Proxy", bg=self.C["surface"], fg=self.C["sub"], font=("Segoe UI", 9))
        self.proxy_badge.pack(side="right", padx=14)

        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=10, pady=10)
        self.t_dl = ttk.Frame(self.nb)
        self.t_pl = ttk.Frame(self.nb)
        self.t_q = ttk.Frame(self.nb)
        self.t_set = ttk.Frame(self.nb)
        self.t_setup = ttk.Frame(self.nb)
        self.nb.add(self.t_dl, text=" Download ")
        self.nb.add(self.t_pl, text=" Playlist ")
        self.nb.add(self.t_q, text=" Queue ")
        self.nb.add(self.t_set, text=" Settings ")
        self.nb.add(self.t_setup, text=" Setup ")
        self._build_download_tab()
        self._build_playlist_tab()
        self._build_queue_tab()
        self._build_settings_tab()
        self._build_setup_tab()

    def _build_download_tab(self):
        left = ttk.Frame(self.t_dl)
        left.pack(side="left", fill="both", expand=True, padx=(10, 4), pady=10)
        right = tk.Frame(self.t_dl, bg=self.C["bg"], width=240)
        right.pack(side="right", fill="y", padx=(0, 10), pady=10)
        right.pack_propagate(False)

        uf = ttk.LabelFrame(left, text="Video / Playlist / Audio URL(s)")
        uf.pack(fill="x", pady=(0, 7))
        self.url_text = tk.Text(uf, height=3, bg=self.C["surface"], fg=self.C["text"], insertbackground=self.C["text"])
        self.url_text.pack(fill="x", padx=5, pady=5)

        ff = ttk.LabelFrame(left, text="Format & Quality")
        ff.pack(fill="x", pady=(0, 7))
        row = ttk.Frame(ff)
        row.pack(fill="x", padx=5, pady=5)
        ttk.Label(row, text="Format:").grid(row=0, column=0, sticky="w")
        self.fmt_var = tk.StringVar(value=self.controller.settings["format"])
        ttk.Combobox(row, textvariable=self.fmt_var, state="readonly", width=24, values=FORMATS).grid(row=0, column=1, padx=5)
        ttk.Label(row, text="Quality:").grid(row=0, column=2, sticky="w", padx=(12, 0))
        self.qual_var = tk.StringVar(value=self.controller.settings["quality"])
        ttk.Combobox(row, textvariable=self.qual_var, state="readonly", width=13, values=list(QUALITY_MAP.keys())).grid(row=0, column=3, padx=5)

        opts = ttk.Frame(ff)
        opts.pack(fill="x", padx=5, pady=(0, 5))
        self.emb_thumb = tk.BooleanVar(value=self.controller.settings["embed_thumbnail"])
        self.emb_subs = tk.BooleanVar(value=self.controller.settings["embed_subs"])
        ttk.Checkbutton(opts, text="Embed Thumbnail", variable=self.emb_thumb).pack(side="left", padx=4)
        ttk.Checkbutton(opts, text="Embed Subtitles", variable=self.emb_subs).pack(side="left", padx=4)

        out = ttk.LabelFrame(left, text="Output")
        out.pack(fill="x", pady=(0, 7))
        self.folder_var = tk.StringVar(value=self.controller.settings["save_folder"])
        self.fname_var = tk.StringVar(value=self.controller.settings["filename_template"])
        ttk.Entry(out, textvariable=self.folder_var).pack(fill="x", padx=5, pady=(5, 3))
        ttk.Entry(out, textvariable=self.fname_var).pack(fill="x", padx=5, pady=(0, 5))

        prog = ttk.LabelFrame(left, text="Progress")
        prog.pack(fill="x", pady=(0, 7))
        self.prog_var = tk.DoubleVar()
        ttk.Progressbar(prog, variable=self.prog_var, maximum=100).pack(fill="x", padx=5, pady=5)
        self.status_lbl = tk.Label(prog, text="Ready", bg=self.C["bg"], fg=self.C["sub"])
        self.status_lbl.pack(anchor="w", padx=5, pady=(0, 5))

        actions = ttk.Frame(left)
        actions.pack(fill="x", pady=(0, 6))
        ttk.Button(actions, text="Fetch Info", command=self.controller.fetch_info_clicked).pack(side="left", padx=(0, 5))
        ttk.Button(actions, text="Download", style="Green.TButton", command=self.controller.start_download_clicked).pack(side="left", padx=(0, 5))
        ttk.Button(actions, text="Add to Queue", command=self.controller.add_to_queue_clicked).pack(side="left", padx=(0, 5))
        ttk.Button(actions, text="Preview Command", command=self.controller.preview_command_clicked).pack(side="left")

        logf = ttk.LabelFrame(left, text="Log")
        logf.pack(fill="both", expand=True)
        self.log = tk.Text(logf, bg=self.C["surface"], fg=self.C["green"], font=("Consolas", 8), state="disabled")
        self.log.pack(fill="both", expand=True, padx=4, pady=4)

        prev = ttk.LabelFrame(right, text="Preview")
        prev.pack(fill="x")
        self.thumb_lbl = tk.Label(prev, bg=self.C["surface"], text="No preview yet", fg=self.C["sub"], width=24, height=7)
        self.thumb_lbl.pack(padx=4, pady=4)
        self.info_box = tk.Text(right, height=18, bg=self.C["surface"], fg=self.C["sub"], state="disabled", wrap="word")
        self.info_box.pack(fill="both", expand=True, pady=8)

    def _build_playlist_tab(self):
        ttk.Label(self.t_pl, text="Playlist URL").pack(anchor="w", padx=10, pady=(10, 4))
        self.pl_url_var = tk.StringVar()
        ttk.Entry(self.t_pl, textvariable=self.pl_url_var).pack(fill="x", padx=10)
        ttk.Button(self.t_pl, text="Load Playlist", command=self.controller.load_playlist_clicked).pack(anchor="w", padx=10, pady=8)
        cols = ("Index", "Title", "Duration")
        self.playlist_tree = ttk.Treeview(self.t_pl, columns=cols, show="headings", height=18)
        for c in cols:
            self.playlist_tree.heading(c, text=c)
        self.playlist_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _build_queue_tab(self):
        cols = ("URL", "Status", "Format", "Progress")
        self.q_tree = ttk.Treeview(self.t_q, columns=cols, show="headings", height=20)
        for c in cols:
            self.q_tree.heading(c, text=c)
        self.q_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def _build_settings_tab(self):
        ttk.Label(self.t_set, text="Settings defaults are wired from config.py and controller state.").pack(anchor="w", padx=10, pady=10)

    def _build_setup_tab(self):
        ttk.Button(self.t_setup, text="Re-check Tools", command=self.controller.check_tools_clicked).pack(anchor="w", padx=10, pady=10)
        self.setup_text = tk.Text(self.t_setup, bg=self.C["surface"], fg=self.C["text"], height=20)
        self.setup_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def get_urls(self):
        raw = self.url_text.get("1.0", "end").strip()
        return [u.strip() for u in raw.splitlines() if u.strip()]

    def append_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def set_status(self, text):
        self.status_lbl.configure(text=text)

    def set_info_text(self, text):
        self.info_box.configure(state="normal")
        self.info_box.delete("1.0", "end")
        self.info_box.insert("1.0", text)
        self.info_box.configure(state="disabled")

    def set_tools_result(self, results):
        ok = results.get("yt-dlp") and results.get("ffmpeg")
        self.tool_badge.configure(text="✅ yt-dlp + ffmpeg ready" if ok else f"❌ Missing: {', '.join([k for k,v in results.items() if not v])}")
        self.setup_text.delete("1.0", "end")
        self.setup_text.insert("1.0", "pip install -U yt-dlp\nInstall ffmpeg via system package manager\npip install pillow\n\nDetected:\n" + "\n".join(f"{k}: {'OK' if v else 'Missing'}" for k, v in results.items()))
