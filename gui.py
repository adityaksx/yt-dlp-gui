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
        self.root.geometry("1340x920")
        self.root.minsize(1100, 800)
        self.root.configure(bg=self.C["bg"])

        # Combobox dropdown list styling overrides
        self.root.option_add("*TCombobox*Listbox.background", self.C["surface"])
        self.root.option_add("*TCombobox*Listbox.foreground", self.C["text"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", self.C["blue"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#001018")

        # Rebuilt Global Window Scroll Architecture
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)

        self.outer_canvas = tk.Canvas(self.main_container, bg=self.C["bg"], highlightthickness=0)
        self.outer_canvas.pack(side="left", fill="both", expand=True)

        self.outer_scroll = ttk.Scrollbar(self.main_container, orient="vertical", command=self.outer_canvas.yview)
        self.outer_scroll.pack(side="right", fill="y")
        self.outer_canvas.configure(yscrollcommand=self.outer_scroll.set)

        self.content = ttk.Frame(self.outer_canvas)
        self.content_id = self.outer_canvas.create_window((0, 0), window=self.content, anchor="nw")

        # Responsive layout bindings
        self.content.bind("<Configure>", self._on_content_configure)
        self.outer_canvas.bind("<Configure>", self._on_canvas_configure)

        # Enable mouse wheel scrolling everywhere on the container
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_content_configure(self, event):
        self.outer_canvas.configure(scrollregion=self.outer_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.outer_canvas.itemconfigure(self.content_id, width=event.width)

    def _on_mousewheel(self, event):
        # Support for multi-platform canvas scroll redirection
        if self.outer_canvas.winfo_exists():
            self.outer_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        c = self.C

        s.configure(".", background=c["bg"], foreground=c["text"], font=("Segoe UI", 10))
        s.configure("Card.TFrame", background=c["surface"])
        s.configure("TFrame", background=c["bg"])
        s.configure("TLabel", background=c["bg"], foreground=c["text"])
        s.configure("Sub.TLabel", background=c["bg"], foreground=c["sub"], font=("Segoe UI", 9))

        s.configure("TLabelframe", background=c["bg"], bordercolor=c["border"], relief="solid", borderwidth=1)
        s.configure("TLabelframe.Label", background=c["bg"], foreground=c["blue"], font=("Segoe UI", 10, "bold"))

        s.configure("TEntry", fieldbackground=c["surface2"], foreground=c["text"], insertcolor=c["text"], borderwidth=0)
        s.configure("TCombobox", fieldbackground=c["surface2"], foreground=c["text"], borderwidth=0)
        s.configure("TSpinbox", fieldbackground=c["surface2"], foreground=c["text"], borderwidth=0)

        s.configure("Accent.TButton", background=c["blue"], foreground="#001018", borderwidth=0, font=("Segoe UI", 10, "bold"))
        s.configure("Success.TButton", background=c["green"], foreground="#02130a", borderwidth=0, font=("Segoe UI", 10, "bold"))
        s.configure("Warn.TButton", background=c["amber"], foreground="#1f1300", borderwidth=0, font=("Segoe UI", 10))
        s.configure("Danger.TButton", background=c["red"], foreground="#180303", borderwidth=0, font=("Segoe UI", 10))

        s.configure("TNotebook", background=c["bg"], borderwidth=0)
        s.configure("TNotebook.Tab", background=c["surface2"], foreground=c["text"], padding=[20, 10], font=("Segoe UI", 10))
        s.map("TNotebook.Tab", background=[("selected", c["blue"])], foreground=[("selected", "#001018")])

        s.configure("TProgressbar", troughcolor=c["surface2"], background=c["blue"], borderwidth=0)
        s.configure("Treeview", background=c["surface"], foreground=c["text"], fieldbackground=c["surface"], rowheight=30, borderwidth=0)
        s.configure("Treeview.Heading", background=c["surface2"], foreground=c["blue"], font=("Segoe UI", 10, "bold"), borderwidth=0)

    def _build(self):
        self._build_header()

        self.nb = ttk.Notebook(self.content)
        self.nb.pack(fill="both", expand=True, padx=16, pady=8)

        self.tab_download = ttk.Frame(self.nb)
        self.tab_playlist = ttk.Frame(self.nb)
        self.tab_queue = ttk.Frame(self.nb)
        self.tab_settings = ttk.Frame(self.nb)
        self.tab_setup = ttk.Frame(self.nb)

        self.nb.add(self.tab_download, text="📥 Download Dashboard")
        self.nb.add(self.tab_playlist, text="🔀 Playlist Manager")
        self.nb.add(self.tab_queue, text="⏳ Tasks Queue")
        self.nb.add(self.tab_settings, text="⚙️ Preferences")
        self.nb.add(self.tab_setup, text="🛠️ System Diagnostics")

        self._build_download_tab()
        self._build_playlist_tab()
        self._build_queue_tab()
        self._build_settings_tab()
        self._build_setup_tab()

    def _build_header(self):
        bar = tk.Frame(self.content, bg=self.C["surface"], height=64)
        bar.pack(fill="x")

        tk.Label(bar, text="yt-dlp Engine Workspace", bg=self.C["surface"], fg=self.C["text"], font=("Segoe UI Semibold", 16)).pack(side="left", padx=20, pady=14)

        self.proxy_badge = tk.Label(bar, text="⚪ No Proxy Active", bg=self.C["surface"], fg=self.C["sub"], font=("Segoe UI", 10))
        self.proxy_badge.pack(side="right", padx=20)

        self.tool_badge = tk.Label(bar, text="System Ready", bg=self.C["surface"], fg=self.C["blue"], font=("Segoe UI", 10, "bold"))
        self.tool_badge.pack(side="right", padx=20)

    def _build_download_tab(self):
        # Functional split panels
        left = ttk.Frame(self.tab_download)
        right = ttk.Frame(self.tab_download)
        left.pack(side="left", fill="both", expand=True, padx=(4, 10), pady=10)
        right.pack(side="right", fill="y", padx=(10, 4), pady=10)

        # 1. Scope Resource Target URL Input
        urls = ttk.LabelFrame(left, text=" Stream Resource Targets (Single URL or one per line) ")
        urls.pack(fill="x", pady=(0, 12))
        self.url_text = tk.Text(urls, height=4, bg=self.C["surface"], fg=self.C["text"], insertbackground=self.C["text"], relief="flat", font=("Consolas", 10), padx=8, pady=8)
        self.url_text.pack(fill="x", padx=10, pady=10)

        # 2. Output and Format Configuration Grid
        fmt = ttk.LabelFrame(left, text=" Extraction and Target Container Profiles ")
        fmt.pack(fill="x", pady=(0, 12))

        grid = ttk.Frame(fmt)
        grid.pack(fill="x", padx=10, pady=10)
        grid.columnconfigure(1, weight=1)
        grid.columnconfigure(3, weight=1)

        ttk.Label(grid, text="Codec Format").grid(row=0, column=0, sticky="w", pady=6)
        self.fmt_var = tk.StringVar(value=self.controller.settings["format"])
        ttk.Combobox(grid, textvariable=self.fmt_var, state="readonly", values=FORMATS).grid(row=0, column=1, sticky="ew", padx=(8, 16), pady=6)

        ttk.Label(grid, text="Resolution Max").grid(row=0, column=2, sticky="w", pady=6)
        self.qual_var = tk.StringVar(value=self.controller.settings["quality"])
        ttk.Combobox(grid, textvariable=self.qual_var, state="readonly", values=list(QUALITY_MAP.keys())).grid(row=0, column=3, sticky="ew", padx=(8, 0), pady=6)

        ttk.Label(grid, text="Destination").grid(row=1, column=0, sticky="w", pady=6)
        self.folder_var = tk.StringVar(value=self.controller.settings["save_folder"])
        ttk.Entry(grid, textvariable=self.folder_var).grid(row=1, column=1, columnspan=2, sticky="ew", padx=(8, 12), pady=6)
        ttk.Button(grid, text="Browse...", command=self._pick_folder, width=10).grid(row=1, column=3, sticky="w", pady=6)

        ttk.Label(grid, text="Naming Logic").grid(row=2, column=0, sticky="w", pady=6)
        self.fname_var = tk.StringVar(value=self.controller.settings["filename_template"])
        ttk.Entry(grid, textvariable=self.fname_var).grid(row=2, column=1, columnspan=3, sticky="ew", padx=(8, 0), pady=6)

        # Checkbutton Flags Switchboard
        self.embed_thumb_var = tk.BooleanVar(value=True)
        self.embed_subs_var = tk.BooleanVar(value=False)
        self.embed_meta_var = tk.BooleanVar(value=True)
        self.all_audio_var = tk.BooleanVar(value=False)
        self.sponsor_var = tk.BooleanVar(value=False)
        self.sub_auto_var = tk.BooleanVar(value=True)

        opts = ttk.Frame(fmt)
        opts.pack(fill="x", padx=10, pady=(4, 10))
        ttk.Checkbutton(opts, text="Inject Thumbnail", variable=self.embed_thumb_var).pack(side="left", padx=(0, 12))
        ttk.Checkbutton(opts, text="Burn Subtitles", variable=self.embed_subs_var).pack(side="left", padx=(0, 12))
        ttk.Checkbutton(opts, text="Write Metadata Tags", variable=self.embed_meta_var).pack(side="left", padx=(0, 12))
        ttk.Checkbutton(opts, text="Keep Multi-Audio", variable=self.all_audio_var).pack(side="left", padx=(0, 12))
        ttk.Checkbutton(opts, text="SponsorBlock Filter", variable=self.sponsor_var).pack(side="left")

        # 3. Dynamic Language Selection Panels
        langs = ttk.LabelFrame(left, text=" Localization Elements ")
        langs.pack(fill="x", pady=(0, 12))
        lrow = ttk.Frame(langs)
        lrow.pack(fill="x", padx=10, pady=10)
        lrow.columnconfigure(0, weight=1)
        lrow.columnconfigure(1, weight=1)

        ttk.Label(lrow, text="Prioritize Audio Stream Language").grid(row=0, column=0, sticky="w")
        self.audio_lang_list = tk.Listbox(lrow, selectmode="multiple", exportselection=False, height=4, bg=self.C["surface"], fg=self.C["text"], selectbackground=self.C["blue"], selectforeground="#001018", relief="flat", highlightthickness=0)
        self.audio_lang_list.grid(row=1, column=0, sticky="nsew", padx=(0, 16), pady=(6, 0))

        ttk.Label(lrow, text="Download Track Subtitles").grid(row=0, column=1, sticky="w")
        self.sub_lang_list = tk.Listbox(lrow, selectmode="multiple", exportselection=False, height=4, bg=self.C["surface"], fg=self.C["text"], selectbackground=self.C["blue"], selectforeground="#001018", relief="flat", highlightthickness=0)
        self.sub_lang_list.grid(row=1, column=1, sticky="nsew", padx=(0, 16), pady=(6, 0))

        right_col = ttk.Frame(lrow)
        right_col.grid(row=1, column=2, sticky="nswn", pady=(4, 0))
        ttk.Label(right_col, text="Subtitle Type").pack(anchor="w")
        self.sub_fmt_var = tk.StringVar(value="srt")
        ttk.Combobox(right_col, textvariable=self.sub_fmt_var, state="readonly", values=SUBTITLE_FORMATS, width=10).pack(anchor="w", pady=(4, 8))
        ttk.Checkbutton(right_col, text="Fetch Auto-Generated", variable=self.sub_auto_var).pack(anchor="w")

        # 4. Engine Process Metrics Panel
        prog = ttk.LabelFrame(left, text=" Stream Telemetry Pipeline ")
        prog.pack(fill="x", pady=(0, 12))
        self.prog_var = tk.DoubleVar(value=0)
        ttk.Progressbar(prog, variable=self.prog_var, maximum=100).pack(fill="x", padx=10, pady=(10, 6))

        row = ttk.Frame(prog)
        row.pack(fill="x", padx=10, pady=(0, 10))
        self.status_lbl = tk.Label(row, text="Status: Pipeline Idle", bg=self.C["bg"], fg=self.C["sub"])
        self.status_lbl.pack(side="left")
        self.speed_lbl = tk.Label(row, text="0.00 MiB/s", bg=self.C["bg"], fg=self.C["blue"], font=("Segoe UI", 10, "bold"))
        self.speed_lbl.pack(side="right")

        # 5. Core Operational Controls Interlocking Dashboard
        actions = ttk.Frame(left)
        actions.pack(fill="x", pady=(0, 12))
        ttk.Button(actions, text="🔍 Interrogate URL", style="Accent.TButton", command=self.controller.fetch_info, padding=8).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="🚀 Fetch Content", style="Success.TButton", command=self.controller.download_now, padding=8).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="⏸️ Pause", style="Warn.TButton", padding=8).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="⏹️ Abort", style="Danger.TButton", padding=8).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="➕ Queue Job", command=self.controller.add_queue, padding=8).pack(side="left", padx=(0, 6))
        ttk.Button(actions, text="⚙️ View Direct Arguments", command=self.controller.preview_command, padding=8).pack(side="left")

        # 6. Rebalanced Long-Form Diagnostic Engine Terminal logs
        logs = ttk.LabelFrame(left, text=" Real-Time Process Standard Output Streams (Extended Logger) ")
        logs.pack(fill="both", expand=True)
        log_wrap = ttk.Frame(logs)
        log_wrap.pack(fill="both", expand=True, padx=10, pady=10)

        # Extended high-capacity visibility metrics console window (height modified from 26 to 42)
        self.log_box = tk.Text(log_wrap, height=42, wrap="none", bg="#040a12", fg="#38bdf8", insertbackground=self.C["text"], relief="flat", font=("Consolas", 9), padx=6, pady=6)
        log_y = ttk.Scrollbar(log_wrap, orient="vertical", command=self.log_box.yview)
        log_x = ttk.Scrollbar(log_wrap, orient="horizontal", command=self.log_box.xview)
        self.log_box.configure(yscrollcommand=log_y.set, xscrollcommand=log_x.set)

        self.log_box.pack(side="left", fill="both", expand=True)
        log_y.pack(side="right", fill="y")
        log_x.pack(side="bottom", fill="x")

        # Right Meta Manifest Context Visual Inspector panel
        prev = ttk.LabelFrame(right, text=" Engine Structural Target Manifest ")
        prev.pack(fill="both", expand=True)
        self.thumb_lbl = tk.Label(prev, text="No Preview Context Available", bg=self.C["surface"], fg=self.C["sub"], width=46, height=14, relief="flat")
        self.thumb_lbl.pack(fill="x", padx=10, pady=10)
        self.info_box = tk.Text(prev, width=42, bg=self.C["surface"], fg=self.C["text"], relief="flat", wrap="word", font=("Segoe UI", 9), padx=6, pady=6)
        self.info_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _build_playlist_tab(self):
        top = ttk.LabelFrame(self.tab_playlist, text=" Multi-Target Processing Node Registry ")
        top.pack(fill="x", padx=8, pady=8)

        row = ttk.Frame(top)
        row.pack(fill="x", padx=10, pady=10)
        self.playlist_url_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.playlist_url_var).pack(side="left", fill="x", expand=True, ipady=4)
        ttk.Button(row, text="Parse Vector Index", style="Accent.TButton", command=self.controller.load_playlist, padding=6).pack(side="left", padx=(10, 0))
        ttk.Button(row, text="Pull Selected Indexes", style="Success.TButton", command=self.controller.download_playlist_selected, padding=6).pack(side="left", padx=(10, 0))

        self.playlist_status = tk.Label(top, text="", bg=self.C["bg"], fg=self.C["sub"])
        self.playlist_status.pack(anchor="w", padx=10, pady=(0, 10))

        cols = ("Pick", "Index", "Title", "Duration", "Uploader")
        self.playlist_tree = ttk.Treeview(self.tab_playlist, columns=cols, show="headings", selectmode="extended")

        # Column alignments optimization
        self.playlist_tree.heading("Pick", text="Status", anchor="w")
        self.playlist_tree.heading("Index", text="Index Pos", anchor="w")
        self.playlist_tree.heading("Title", text="Resource Descriptor Title", anchor="w")
        self.playlist_tree.heading("Duration", text="Length", anchor="w")
        self.playlist_tree.heading("Uploader", text="Channel Context Authority", anchor="w")

        self.playlist_tree.column("Pick", width=70, minwidth=60, stretch=False)
        self.playlist_tree.column("Index", width=90, minwidth=70, stretch=False)
        self.playlist_tree.column("Duration", width=100, minwidth=90, stretch=False)

        self.playlist_tree.pack(fill="both", expand=True, padx=8, pady=8)

    def _build_queue_tab(self):
        cols = ("URL", "Status", "Format", "Progress", "Speed")
        self.queue_tree = ttk.Treeview(self.tab_queue, columns=cols, show="headings")
        for c in cols:
            self.queue_tree.heading(c, text=c, anchor="w")
        self.queue_tree.pack(fill="both", expand=True, padx=8, pady=8)

    def _build_settings_tab(self):
        card = ttk.LabelFrame(self.tab_settings, text=" Primary Engine Runtime Profile Overrides ")
        card.pack(fill="x", padx=8, pady=8)

        g = ttk.Frame(card)
        g.pack(fill="x", padx=12, pady=12)
        g.columnconfigure(1, weight=1)

        ttk.Label(g, text="Default Target Directory").grid(row=0, column=0, sticky="w", pady=6)
        self.settings_folder_var = tk.StringVar(value=self.controller.settings["save_folder"])
        ttk.Entry(g, textvariable=self.settings_folder_var).grid(row=0, column=1, sticky="ew", padx=10, pady=6)

        ttk.Label(g, text="Global Filename Template").grid(row=1, column=0, sticky="w", pady=6)
        self.settings_name_var = tk.StringVar(value=self.controller.settings["filename_template"])
        ttk.Entry(g, textvariable=self.settings_name_var).grid(row=1, column=1, sticky="ew", padx=10, pady=6)

        ttk.Label(g, text="Container Profile Target").grid(row=2, column=0, sticky="w", pady=6)
        self.settings_format_var = tk.StringVar(value=self.controller.settings["format"])
        ttk.Combobox(g, textvariable=self.settings_format_var, state="readonly", values=FORMATS).grid(row=2, column=1, sticky="ew", padx=10, pady=6)

        ttk.Label(g, text="Max Resolution Threshold").grid(row=3, column=0, sticky="w", pady=6)
        self.settings_quality_var = tk.StringVar(value=self.controller.settings["quality"])
        ttk.Combobox(g, textvariable=self.settings_quality_var, state="readonly", values=list(QUALITY_MAP.keys())).grid(row=3, column=1, sticky="ew", padx=10, pady=6)

        ttk.Label(g, text="Proxy Server Address").grid(row=4, column=0, sticky="w", pady=6)
        self.settings_proxy_var = tk.StringVar(value=self.controller.settings.get("proxy", ""))
        ttk.Entry(g, textvariable=self.settings_proxy_var).grid(row=4, column=1, sticky="ew", padx=10, pady=6)

        ttk.Label(g, text="API Player Clients Strategy").grid(row=5, column=0, sticky="w", pady=6)
        self.settings_player_clients_var = tk.StringVar(value=self.controller.settings.get("player_clients", ""))
        ttk.Entry(g, textvariable=self.settings_player_clients_var).grid(row=5, column=1, sticky="ew", padx=10, pady=6)

        ttk.Label(g, text="YT PO token (Bypass)").grid(row=6, column=0, sticky="w", pady=6)
        self.settings_po_token_var = tk.StringVar(value=self.controller.settings.get("po_token", ""))
        ttk.Entry(g, textvariable=self.settings_po_token_var).grid(row=6, column=1, sticky="ew", padx=10, pady=6)

        ttk.Label(g, text="Concurrent Processing Threads").grid(row=7, column=0, sticky="w", pady=6)
        self.settings_concurrent_var = tk.IntVar(value=int(self.controller.settings.get("concurrent_downloads", 2)))
        ttk.Spinbox(g, from_=1, to=10, textvariable=self.settings_concurrent_var, width=12).grid(row=7, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(g, text="Bandwidth Speed Limit (KB/s)").grid(row=8, column=0, sticky="w", pady=6)
        self.settings_speed_var = tk.IntVar(value=int(self.controller.settings.get("speed_limit_kbps", 0)))
        ttk.Spinbox(g, from_=0, to=50000, increment=100, textvariable=self.settings_speed_var, width=12).grid(row=8, column=1, sticky="w", padx=10, pady=6)

        self.settings_tor_var = tk.BooleanVar(value=bool(self.controller.settings.get("prefer_tor", False)))
        ttk.Checkbutton(g, text="Route Through Local Tor Proxy Node Layer", variable=self.settings_tor_var).grid(row=9, column=1, sticky="w", padx=10, pady=8)

        ttk.Button(card, text="🔒 Commit Runtime Architecture Changes", style="Success.TButton", command=self.controller.apply_settings, padding=8).pack(anchor="w", padx=12, pady=(4, 12))

    def _build_setup_tab(self):
        top = ttk.Frame(self.tab_setup)
        top.pack(fill="x", padx=8, pady=8)
        ttk.Button(top, text="Verify Environment Dependencies", style="Accent.TButton", command=self.controller.check_tools, padding=6).pack(side="left")

        self.setup_box = tk.Text(self.tab_setup, bg=self.C["surface"], fg=self.C["text"], relief="flat", font=("Consolas", 10), padx=8, pady=8)
        self.setup_box.pack(fill="both", expand=True, padx=8, pady=8)

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

    def show_format_fallback(self, text):
        self.info_box.delete("1.0", "end")
        self.info_box.insert("1.0", "Requested format failed. Available formats:\n\n" + text)
