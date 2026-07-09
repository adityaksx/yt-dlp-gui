import tkinter as tk
from tkinter import ttk, filedialog
from config import APP_NAME, APP_VERSION, THEME_COLORS, FORMATS, QUALITY_MAP, SUBTITLE_FORMATS


class ModernGUI:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.C = THEME_COLORS
        self.thumb_image = None
        self._setup_window()
        self._setup_styles()
        self._build()

    def _setup_window(self):
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        self.root.geometry("1320x860")
        self.root.minsize(1080, 760)
        self.root.configure(bg=self.C["bg"])

    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        c = self.C
        s.configure(".", background=c["bg"], foreground=c["text"], font=("Segoe UI", 10))
        s.configure("Card.TFrame", background=c["surface"])
        s.configure("TFrame", background=c["bg"])
        s.configure("TLabel", background=c["bg"], foreground=c["text"])
        s.configure("Sub.TLabel", background=c["bg"], foreground=c["sub"], font=("Segoe UI", 9))
        s.configure("TLabelframe", background=c["bg"], bordercolor=c["border"])
        s.configure("TLabelframe.Label", background=c["bg"], foreground=c["blue"], font=("Segoe UI", 10, "bold"))
        s.configure("TEntry", fieldbackground=c["surface2"], foreground=c["text"], insertcolor=c["text"])
        s.configure("TCombobox", fieldbackground=c["surface2"], foreground=c["text"])
        s.configure("Accent.TButton", background=c["blue"], foreground="#001018", borderwidth=0)
        s.configure("Success.TButton", background=c["green"], foreground="#02130a", borderwidth=0)
        s.configure("Warn.TButton", background=c["amber"], foreground="#1f1300", borderwidth=0)
        s.configure("Danger.TButton", background=c["red"], foreground="#180303", borderwidth=0)
        s.configure("TNotebook", background=c["bg"], borderwidth=0)
        s.configure("TNotebook.Tab", background=c["surface2"], foreground=c["text"], padding=[16, 9])
        s.map("TNotebook.Tab", background=[("selected", c["blue"])], foreground=[("selected", "#001018")])
        s.configure("TProgressbar", troughcolor=c["surface2"], background=c["blue"], borderwidth=0)
        s.configure("Treeview", background=c["surface"], foreground=c["text"], fieldbackground=c["surface"], rowheight=28)
        s.configure("Treeview.Heading", background=c["surface2"], foreground=c["blue"], font=("Segoe UI", 10, "bold"))

    def _build(self):
        self._build_header()
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True, padx=12, pady=12)
        self.tab_download = ttk.Frame(self.nb)
        self.tab_playlist = ttk.Frame(self.nb)
        self.tab_queue = ttk.Frame(self.nb)
        self.tab_settings = ttk.Frame(self.nb)
        self.tab_setup = ttk.Frame(self.nb)
        self.nb.add(self.tab_download, text="Download")
        self.nb.add(self.tab_playlist, text="Playlist")
        self.nb.add(self.tab_queue, text="Queue")
        self.nb.add(self.tab_settings, text="Settings")
        self.nb.add(self.tab_setup, text="Setup")
        self._build_download_tab()
        self._build_playlist_tab()
        self._build_queue_tab()
        self._build_settings_tab()
        self._build_setup_tab()

    def _build_header(self):
        bar = tk.Frame(self.root, bg=self.C["surface"], height=56)
        bar.pack(fill="x")
        tk.Label(bar, text="yt-dlp Modern GUI", bg=self.C["surface"], fg=self.C["text"], font=("Segoe UI Semibold", 16)).pack(side="left", padx=16, pady=12)
        self.proxy_badge = tk.Label(bar, text="⚪ No Proxy", bg=self.C["surface"], fg=self.C["sub"], font=("Segoe UI", 10))
        self.proxy_badge.pack(side="right", padx=16)
        self.tool_badge = tk.Label(bar, text="Ready", bg=self.C["surface"], fg=self.C["blue"], font=("Segoe UI", 10, "bold"))
        self.tool_badge.pack(side="right", padx=16)

    def _build_download_tab(self):
        left = ttk.Frame(self.tab_download)
        right = ttk.Frame(self.tab_download)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=4)
        right.pack(side="right", fill="y", padx=(8, 0), pady=4)

        urls = ttk.LabelFrame(left, text="Video / Playlist / Audio URL")
        urls.pack(fill="x", pady=(0, 8))
        self.url_text = tk.Text(urls, height=4, bg=self.C["surface"], fg=self.C["text"], insertbackground=self.C["text"], relief="flat")
        self.url_text.pack(fill="x", padx=8, pady=8)

        fmt = ttk.LabelFrame(left, text="Download options")
        fmt.pack(fill="x", pady=(0, 8))
        grid = ttk.Frame(fmt)
        grid.pack(fill="x", padx=8, pady=8)
        ttk.Label(grid, text="Format").grid(row=0, column=0, sticky="w")
        self.fmt_var = tk.StringVar(value=self.controller.settings["format"])
        ttk.Combobox(grid, textvariable=self.fmt_var, state="readonly", values=FORMATS, width=24).grid(row=0, column=1, sticky="ew", padx=(6, 12))
        ttk.Label(grid, text="Quality").grid(row=0, column=2, sticky="w")
        self.qual_var = tk.StringVar(value=self.controller.settings["quality"])
        ttk.Combobox(grid, textvariable=self.qual_var, state="readonly", values=list(QUALITY_MAP.keys()), width=12).grid(row=0, column=3, sticky="ew", padx=(6, 0))

        ttk.Label(grid, text="Folder").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.folder_var = tk.StringVar(value=self.controller.settings["save_folder"])
        ttk.Entry(grid, textvariable=self.folder_var).grid(row=1, column=1, columnspan=2, sticky="ew", padx=(6, 12), pady=(10, 0))
        ttk.Button(grid, text="Browse", command=self._pick_folder).grid(row=1, column=3, pady=(10, 0))
        ttk.Label(grid, text="Filename").grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.fname_var = tk.StringVar(value=self.controller.settings["filename_template"])
        ttk.Entry(grid, textvariable=self.fname_var).grid(row=2, column=1, columnspan=3, sticky="ew", padx=(6, 0), pady=(10, 0))

        self.embed_thumb_var = tk.BooleanVar(value=True)
        self.embed_subs_var = tk.BooleanVar(value=False)
        self.embed_meta_var = tk.BooleanVar(value=True)
        self.all_audio_var = tk.BooleanVar(value=False)
        self.sponsor_var = tk.BooleanVar(value=False)
        self.sub_auto_var = tk.BooleanVar(value=True)
        opts = ttk.Frame(fmt)
        opts.pack(fill="x", padx=8, pady=(0, 8))
        ttk.Checkbutton(opts, text="Embed thumbnail", variable=self.embed_thumb_var).pack(side="left", padx=(0, 8))
        ttk.Checkbutton(opts, text="Embed subtitle", variable=self.embed_subs_var).pack(side="left", padx=(0, 8))
        ttk.Checkbutton(opts, text="Embed metadata", variable=self.embed_meta_var).pack(side="left", padx=(0, 8))
        ttk.Checkbutton(opts, text="All audio languages", variable=self.all_audio_var).pack(side="left", padx=(0, 8))
        ttk.Checkbutton(opts, text="SponsorBlock", variable=self.sponsor_var).pack(side="left")

        langs = ttk.LabelFrame(left, text="Language options")
        langs.pack(fill="x", pady=(0, 8))
        lrow = ttk.Frame(langs)
        lrow.pack(fill="x", padx=8, pady=8)
        ttk.Label(lrow, text="Audio languages").grid(row=0, column=0, sticky="w")
        self.audio_lang_list = tk.Listbox(lrow, selectmode="multiple", exportselection=False, height=5, bg=self.C["surface"], fg=self.C["text"], relief="flat")
        self.audio_lang_list.grid(row=1, column=0, sticky="nsew", padx=(0, 12), pady=(4, 0))
        ttk.Label(lrow, text="Subtitle languages").grid(row=0, column=1, sticky="w")
        self.sub_lang_list = tk.Listbox(lrow, selectmode="multiple", exportselection=False, height=5, bg=self.C["surface"], fg=self.C["text"], relief="flat")
        self.sub_lang_list.grid(row=1, column=1, sticky="nsew", padx=(0, 12), pady=(4, 0))
        right_col = ttk.Frame(lrow)
        right_col.grid(row=1, column=2, sticky="nsw", pady=(4, 0))
        ttk.Label(right_col, text="Subtitle format").pack(anchor="w")
        self.sub_fmt_var = tk.StringVar(value="srt")
        ttk.Combobox(right_col, textvariable=self.sub_fmt_var, state="readonly", values=SUBTITLE_FORMATS, width=8).pack(anchor="w", pady=(4, 10))
        ttk.Checkbutton(right_col, text="Include auto-generated", variable=self.sub_auto_var).pack(anchor="w")

        prog = ttk.LabelFrame(left, text="Progress")
        prog.pack(fill="x", pady=(0, 8))
        self.prog_var = tk.DoubleVar(value=0)
        ttk.Progressbar(prog, variable=self.prog_var, maximum=100).pack(fill="x", padx=8, pady=(8, 4))
        row = ttk.Frame(prog)
        row.pack(fill="x", padx=8, pady=(0, 8))
        self.status_lbl = tk.Label(row, text="Ready", bg=self.C["bg"], fg=self.C["sub"])
        self.status_lbl.pack(side="left")
        self.speed_lbl = tk.Label(row, text="", bg=self.C["bg"], fg=self.C["blue"])
        self.speed_lbl.pack(side="right")

        actions = ttk.Frame(left)
        actions.pack(fill="x", pady=(0, 8))
        ttk.Button(actions, text="Fetch Info", style="Accent.TButton", command=self.controller.fetch_info).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Download", style="Success.TButton", command=self.controller.download_now).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Pause", style="Warn.TButton").pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Cancel", style="Danger.TButton").pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Add to Queue", command=self.controller.add_queue).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="Preview Command", command=self.controller.preview_command).pack(side="left")

        logs = ttk.LabelFrame(left, text="Log")
        logs.pack(fill="both", expand=True)
        self.log_box = tk.Text(logs, height=10, bg="#08111f", fg="#7dd3fc", insertbackground=self.C["text"], relief="flat")
        self.log_box.pack(fill="both", expand=True, padx=8, pady=8)

        prev = ttk.LabelFrame(right, text="Preview")
        prev.pack(fill="both", expand=True)
        self.thumb_lbl = tk.Label(prev, text="No preview", bg=self.C["surface"], fg=self.C["sub"], width=42, height=12)
        self.thumb_lbl.pack(fill="x", padx=8, pady=8)
        self.info_box = tk.Text(prev, width=38, bg=self.C["surface"], fg=self.C["text"], relief="flat", wrap="word")
        self.info_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _build_playlist_tab(self):
        top = ttk.LabelFrame(self.tab_playlist, text="Playlist")
        top.pack(fill="x", padx=4, pady=(4, 8))
        row = ttk.Frame(top)
        row.pack(fill="x", padx=8, pady=8)
        self.playlist_url_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.playlist_url_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Load", style="Accent.TButton", command=self.controller.load_playlist).pack(side="left", padx=(8, 0))
        ttk.Button(row, text="Download Selected", style="Success.TButton", command=self.controller.download_playlist_selected).pack(side="left", padx=(8, 0))
        self.playlist_status = tk.Label(top, text="", bg=self.C["bg"], fg=self.C["sub"])
        self.playlist_status.pack(anchor="w", padx=8, pady=(0, 8))
        cols = ("Pick", "Index", "Title", "Duration", "Uploader")
        self.playlist_tree = ttk.Treeview(self.tab_playlist, columns=cols, show="headings", selectmode="extended")
        for c in cols:
            self.playlist_tree.heading(c, text=c)
        self.playlist_tree.pack(fill="both", expand=True, padx=4, pady=4)

    def _build_queue_tab(self):
        cols = ("URL", "Status", "Format", "Progress", "Speed")
        self.queue_tree = ttk.Treeview(self.tab_queue, columns=cols, show="headings")
        for c in cols:
            self.queue_tree.heading(c, text=c)
        self.queue_tree.pack(fill="both", expand=True, padx=4, pady=4)

    def _build_settings_tab(self):
        card = ttk.LabelFrame(self.tab_settings, text="Default settings")
        card.pack(fill="x", padx=4, pady=4)
        g = ttk.Frame(card)
        g.pack(fill="x", padx=8, pady=8)
        ttk.Label(g, text="Default folder").grid(row=0, column=0, sticky="w")
        self.settings_folder_var = tk.StringVar(value=self.controller.settings["save_folder"])
        ttk.Entry(g, textvariable=self.settings_folder_var).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Label(g, text="Filename template").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.settings_name_var = tk.StringVar(value=self.controller.settings["filename_template"])
        ttk.Entry(g, textvariable=self.settings_name_var).grid(row=1, column=1, sticky="ew", padx=8, pady=(8, 0))
        ttk.Label(g, text="Default format").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.settings_format_var = tk.StringVar(value=self.controller.settings["format"])
        ttk.Combobox(g, textvariable=self.settings_format_var, state="readonly", values=FORMATS).grid(row=2, column=1, sticky="ew", padx=8, pady=(8, 0))
        ttk.Label(g, text="Default quality").grid(row=3, column=0, sticky="w", pady=(8, 0))
        self.settings_quality_var = tk.StringVar(value=self.controller.settings["quality"])
        ttk.Combobox(g, textvariable=self.settings_quality_var, state="readonly", values=list(QUALITY_MAP.keys())).grid(row=3, column=1, sticky="ew", padx=8, pady=(8, 0))
        ttk.Label(g, text="Proxy").grid(row=4, column=0, sticky="w", pady=(8, 0))
        self.settings_proxy_var = tk.StringVar(value=self.controller.settings.get("proxy", ""))
        ttk.Entry(g, textvariable=self.settings_proxy_var).grid(row=4, column=1, sticky="ew", padx=8, pady=(8, 0))
        ttk.Label(g, text="Player clients").grid(row=5, column=0, sticky="w", pady=(8, 0))
        self.settings_player_clients_var = tk.StringVar(value=self.controller.settings.get("player_clients", "android,web"))
        ttk.Entry(g, textvariable=self.settings_player_clients_var).grid(row=5, column=1, sticky="ew", padx=8, pady=(8, 0))
        ttk.Label(g, text="Concurrent downloads").grid(row=6, column=0, sticky="w", pady=(8, 0))
        self.settings_concurrent_var = tk.IntVar(value=int(self.controller.settings.get("concurrent_downloads", 2)))
        ttk.Spinbox(g, from_=1, to=10, textvariable=self.settings_concurrent_var).grid(row=6, column=1, sticky="w", padx=8, pady=(8, 0))
        ttk.Label(g, text="Speed limit (KB/s)").grid(row=7, column=0, sticky="w", pady=(8, 0))
        self.settings_speed_var = tk.IntVar(value=int(self.controller.settings.get("speed_limit_kbps", 0)))
        ttk.Spinbox(g, from_=0, to=50000, increment=100, textvariable=self.settings_speed_var).grid(row=7, column=1, sticky="w", padx=8, pady=(8, 0))
        self.settings_tor_var = tk.BooleanVar(value=bool(self.controller.settings.get("prefer_tor", False)))
        ttk.Checkbutton(g, text="Use Tor proxy by default", variable=self.settings_tor_var).grid(row=8, column=1, sticky="w", padx=8, pady=(8, 0))
        ttk.Button(card, text="Save Settings", style="Success.TButton", command=self.controller.apply_settings).pack(anchor="w", padx=8, pady=(0, 8))

    def _build_setup_tab(self):
        top = ttk.Frame(self.tab_setup)
        top.pack(fill="x", padx=4, pady=4)
        ttk.Button(top, text="Check Tools", style="Accent.TButton", command=self.controller.check_tools).pack(side="left")
        self.setup_box = tk.Text(self.tab_setup, bg=self.C["surface"], fg=self.C["text"], relief="flat")
        self.setup_box.pack(fill="both", expand=True, padx=4, pady=4)

    def _pick_folder(self):
        folder = filedialog.askdirectory(initialdir=self.folder_var.get() or "/")
        if folder:
            self.folder_var.set(folder)

    def set_thumbnail(self, photo):
        self.thumb_image = photo
        self.thumb_lbl.configure(image=photo, text="")

    def update_info_box(self, info):
        txt = (
            f"Title: {info.title}\n\n"
            f"Type: {info.source_type}\n"
            f"Duration: {info.duration}\n"
            f"Uploader: {info.uploader}\n"
            f"Views: {info.view_count:,}\n"
            f"Likes: {info.like_count:,}\n"
            f"Upload date: {info.upload_date}\n"
            f"Audio langs: {', '.join(info.audio_languages) or '—'}\n"
            f"Subs: {', '.join(info.subtitles_manual) or '—'}\n"
            f"Auto subs: {', '.join(info.subtitles_auto) or '—'}\n"
        )
        self.info_box.delete("1.0", "end")
        self.info_box.insert("1.0", txt)

    def append_log(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def set_status(self, text):
        self.status_lbl.configure(text=text)

    def set_speed(self, text):
        self.speed_lbl.configure(text=text)

    def set_progress(self, value):
        self.prog_var.set(value)

    def set_proxy_text(self, text):
        self.proxy_badge.configure(text=text)

    def set_detected_languages(self, audio_langs, sub_langs, auto_subs):
        self.audio_lang_list.delete(0, "end")
        self.sub_lang_list.delete(0, "end")
        for lang in audio_langs or ["original"]:
            self.audio_lang_list.insert("end", lang)
        subs = list(sub_langs or [])
        if "en" not in subs:
            subs.insert(0, "en")
        for lang in subs or ["en"]:
            self.sub_lang_list.insert("end", lang)
        if self.audio_lang_list.size() > 0:
            self.audio_lang_list.selection_set(0)
        if self.sub_lang_list.size() > 0:
            try:
                en_index = subs.index("en")
            except Exception:
                en_index = 0
            self.sub_lang_list.selection_set(en_index)

    def get_selected_audio_langs(self):
        return [self.audio_lang_list.get(i) for i in self.audio_lang_list.curselection()]

    def get_selected_subtitle_langs(self):
        return [self.sub_lang_list.get(i) for i in self.sub_lang_list.curselection()]

    def populate_playlist(self, items):
        for row in self.playlist_tree.get_children():
            self.playlist_tree.delete(row)
        for i, item in enumerate(items, 1):
            self.playlist_tree.insert("", "end", values=("✔", i, item.get("title", "Untitled"), item.get("duration_string", ""), item.get("uploader") or item.get("channel") or ""))

    def get_selected_playlist_indices(self):
        selected = []
        for item_id in self.playlist_tree.selection():
            values = self.playlist_tree.item(item_id, "values")
            if values:
                selected.append(int(values[1]))
        return selected

    def set_playlist_status(self, text):
        self.playlist_status.configure(text=text)

    def queue_add_row(self, url, status, fmt, progress, speed):
        self.queue_tree.insert("", "end", values=(url, status, fmt, progress, speed))

    def queue_update_row(self, url, status, progress, speed):
        for item in self.queue_tree.get_children():
            values = self.queue_tree.item(item, "values")
            if values and values[0] == url:
                self.queue_tree.item(item, values=(url, status, values[2], progress, speed))
                break

    def show_setup(self, results, install_text):
        good = results.get("yt-dlp") and results.get("ffmpeg")
        self.tool_badge.configure(text="Ready" if good else "Missing tools", fg=self.C["green"] if good else self.C["amber"])
        self.setup_box.delete("1.0", "end")
        self.setup_box.insert("1.0", install_text + "\nDetected:\n" + "\n".join(f"{k}: {'OK' if v else 'Missing'}" for k, v in results.items()))
