import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess, threading, os, json, time, socket, io, re, urllib.request
from datetime import datetime

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ── Config paths ──────────────────────────────────────────────────────────────
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".ytdlp_pro_settings.json")
HISTORY_FILE  = os.path.join(os.path.expanduser("~"), ".ytdlp_pro_history.json")

DEFAULT_SETTINGS = {
    "save_folder":       os.path.expanduser("~/Downloads"),
    "format":            "Best MP4",
    "quality":           "Best",
    "filename_template": "%(title)s.%(ext)s",
    "fragments":         "5",
    "embed_thumbnail":   False,
    "embed_subs":        False,
    "sub_lang":          "en",
    "cookie_file":       "",
    "speed_limit":       "0",
}

C = {   # Catppuccin Mocha palette
    "bg":       "#1e1e2e",
    "surface":  "#313244",
    "surface2": "#45475a",
    "text":     "#cdd6f4",
    "sub":      "#a6adc8",
    "blue":     "#89b4fa",
    "green":    "#a6e3a1",
    "red":      "#f38ba8",
    "yellow":   "#f9e2af",
    "mauve":    "#cba6f7",
    "teal":     "#94e2d5",
}

QUALITY_MAP = {
    "Best": None,
    "4K (2160p)": 2160,
    "1080p": 1080,
    "720p": 720,
    "480p": 480,
    "360p": 360,
    "240p": 240,
}

# ── Main App ──────────────────────────────────────────────────────────────────
class YtDlpPro:
    def __init__(self, root):
        self.root = root
        self.root.title("yt-dlp Pro")
        self.root.geometry("860x680")
        self.root.configure(bg=C["bg"])
        self.root.resizable(True, True)

        self.settings        = self._load_json(SETTINGS_FILE, DEFAULT_SETTINGS)
        self.history         = self._load_json(HISTORY_FILE, [])
        self.download_process = None
        self.is_downloading  = False
        self.active_proxy    = ""
        self.tor_active      = False

        self._setup_styles()
        self._build_ui()

    # ── Persistence ───────────────────────────────────────────────────────────
    def _load_json(self, path, default):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    if isinstance(default, dict):
                        d = default.copy(); d.update(json.load(f)); return d
                    return json.load(f)
            except Exception:
                pass
        return default.copy() if isinstance(default, dict) else list(default)

    def _save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def save_settings(self):
        self._save_json(SETTINGS_FILE, self.settings)

    def add_history(self, url, title, status):
        self.history.append({
            "url": url, "title": title, "status": status,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        self._save_json(HISTORY_FILE, self.history[-200:])

    # ── Styles ────────────────────────────────────────────────────────────────
    def _setup_styles(self):
        s = ttk.Style(); s.theme_use("clam")
        s.configure(".",            background=C["bg"],      foreground=C["text"], font=("Segoe UI", 10))
        s.configure("TFrame",       background=C["bg"])
        s.configure("TLabel",       background=C["bg"],      foreground=C["text"])
        s.configure("TLabelframe",  background=C["bg"],      bordercolor=C["surface2"])
        s.configure("TLabelframe.Label", background=C["bg"], foreground=C["blue"], font=("Segoe UI", 10, "bold"))
        s.configure("TEntry",       fieldbackground=C["surface"], foreground=C["text"], insertcolor=C["text"])
        s.configure("TSpinbox",     fieldbackground=C["surface"], foreground=C["text"])
        s.configure("TCombobox",    fieldbackground=C["surface"], foreground=C["text"], selectbackground=C["surface2"])
        s.configure("TCheckbutton", background=C["bg"],      foreground=C["text"])
        s.configure("TButton",      background=C["blue"],    foreground=C["bg"], font=("Segoe UI", 10, "bold"), borderwidth=0)
        s.map("TButton",            background=[("active", C["mauve"])])
        s.configure("Red.TButton",  background=C["red"],     foreground=C["bg"])
        s.map("Red.TButton",        background=[("active", "#ff8fa8")])
        s.configure("Green.TButton",background=C["green"],   foreground=C["bg"])
        s.map("Green.TButton",      background=[("active", "#80d4a0")])
        s.configure("TNotebook",    background=C["bg"],      borderwidth=0)
        s.configure("TNotebook.Tab",background=C["surface"], foreground=C["sub"], padding=[14, 7])
        s.map("TNotebook.Tab",      background=[("selected", C["blue"])], foreground=[("selected", C["bg"])])
        s.configure("TProgressbar", troughcolor=C["surface"], background=C["blue"], borderwidth=0)
        s.configure("Treeview",     background=C["surface"], foreground=C["text"], fieldbackground=C["surface"], rowheight=26)
        s.configure("Treeview.Heading", background=C["surface2"], foreground=C["blue"], font=("Segoe UI", 10, "bold"))
        s.map("Treeview",           background=[("selected", C["blue"])], foreground=[("selected", C["bg"])])
        s.configure("TScrollbar",   background=C["surface2"], troughcolor=C["surface"], borderwidth=0)

    # ── Main UI ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Top bar
        bar = tk.Frame(self.root, bg=C["surface"], height=46)
        bar.pack(fill="x")
        tk.Label(bar, text="▶  yt-dlp Pro", bg=C["surface"],
                 fg=C["blue"], font=("Segoe UI", 13, "bold")).pack(side="left", padx=14, pady=6)
        self.proxy_badge = tk.Label(bar, text="⚪  No Proxy", bg=C["surface"],
                                    fg=C["sub"], font=("Segoe UI", 9))
        self.proxy_badge.pack(side="right", padx=14)

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=10, pady=10)
        self.nb = nb

        self.t_dl   = ttk.Frame(nb); nb.add(self.t_dl,   text="  ⬇ Download  ")
        self.t_q    = ttk.Frame(nb); nb.add(self.t_q,    text="  📋 Queue  ")
        self.t_geo  = ttk.Frame(nb); nb.add(self.t_geo,  text="  🌐 Geo-Bypass  ")
        self.t_hist = ttk.Frame(nb); nb.add(self.t_hist, text="  🕐 History  ")
        self.t_set  = ttk.Frame(nb); nb.add(self.t_set,  text="  ⚙ Settings  ")

        self._tab_download()
        self._tab_queue()
        self._tab_geo()
        self._tab_history()
        self._tab_settings()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — DOWNLOAD
    # ══════════════════════════════════════════════════════════════════════════
    def _tab_download(self):
        t = self.t_dl

        left  = ttk.Frame(t); left.pack(side="left", fill="both", expand=True, padx=(10,4), pady=10)
        right = tk.Frame(t, bg=C["bg"], width=186); right.pack(side="right", fill="y", padx=(0,10), pady=10)
        right.pack_propagate(False)

        # ── Thumbnail panel ──
        tf = ttk.LabelFrame(right, text="Preview"); tf.pack(fill="x")
        self.thumb_lbl = tk.Label(tf, bg=C["surface"], text="No preview\nyet",
                                   fg=C["sub"], width=22, height=7)
        self.thumb_lbl.pack(padx=4, pady=4)
        ttk.Button(right, text="🔍 Fetch Info", command=lambda: threading.Thread(
            target=self._fetch_info, daemon=True).start()).pack(fill="x", pady=2)
        self.info_box = tk.Text(right, height=7, bg=C["surface"], fg=C["sub"],
                                 font=("Segoe UI", 8), wrap="word", state="disabled", borderwidth=0)
        self.info_box.pack(fill="both", expand=True, pady=2)

        # ── URL ──
        uf = ttk.LabelFrame(left, text="Video / Playlist URL"); uf.pack(fill="x", pady=(0,7))
        ur = ttk.Frame(uf); ur.pack(fill="x", padx=5, pady=5)
        self.url_var = tk.StringVar()
        ttk.Entry(ur, textvariable=self.url_var, font=("Segoe UI", 10)).pack(side="left", fill="x", expand=True)
        ttk.Button(ur, text="📋", width=3,
                   command=lambda: self.url_var.set(self.root.clipboard_get())).pack(side="left", padx=3)
        ttk.Button(ur, text="✖", width=3, style="Red.TButton",
                   command=lambda: self.url_var.set("")).pack(side="left")

        # ── Format / Quality ──
        ff = ttk.LabelFrame(left, text="Format & Quality"); ff.pack(fill="x", pady=(0,7))
        fi = ttk.Frame(ff); fi.pack(fill="x", padx=5, pady=5)

        ttk.Label(fi, text="Format:").grid(row=0, column=0, sticky="w")
        self.fmt_var = tk.StringVar(value=self.settings["format"])
        ttk.Combobox(fi, textvariable=self.fmt_var, state="readonly", width=22,
                     values=["Best MP4","Best Quality","Audio Only (MP3)","Audio Only (M4A)",
                             "Video Only","WebM"]).grid(row=0, column=1, padx=5)

        ttk.Label(fi, text="Quality:").grid(row=0, column=2, sticky="w", padx=(12,0))
        self.qual_var = tk.StringVar(value=self.settings["quality"])
        ttk.Combobox(fi, textvariable=self.qual_var, state="readonly", width=13,
                     values=list(QUALITY_MAP.keys())).grid(row=0, column=3, padx=5)

        op = ttk.Frame(ff); op.pack(fill="x", padx=5, pady=(0,5))
        self.emb_thumb = tk.BooleanVar(value=self.settings["embed_thumbnail"])
        self.emb_subs  = tk.BooleanVar(value=self.settings["embed_subs"])
        self.sub_lang  = tk.StringVar(value=self.settings["sub_lang"])
        ttk.Checkbutton(op, text="Embed Thumbnail", variable=self.emb_thumb).pack(side="left", padx=4)
        ttk.Checkbutton(op, text="Embed Subtitles",  variable=self.emb_subs).pack(side="left", padx=4)
        ttk.Label(op, text="Lang:").pack(side="left", padx=(8,2))
        ttk.Entry(op, textvariable=self.sub_lang, width=4).pack(side="left")

        # ── Output ──
        of = ttk.LabelFrame(left, text="Output"); of.pack(fill="x", pady=(0,7))
        oi = ttk.Frame(of); oi.pack(fill="x", padx=5, pady=5)
        self.folder_var = tk.StringVar(value=self.settings["save_folder"])
        self.fname_var  = tk.StringVar(value=self.settings["filename_template"])
        ttk.Label(oi, text="Folder:").grid(row=0, column=0, sticky="w")
        ttk.Entry(oi, textvariable=self.folder_var, width=38).grid(row=0, column=1, padx=4)
        ttk.Button(oi, text="📁", command=self._browse_folder).grid(row=0, column=2)
        ttk.Label(oi, text="Filename:").grid(row=1, column=0, sticky="w", pady=(4,0))
        ttk.Entry(oi, textvariable=self.fname_var, width=38).grid(row=1, column=1, padx=4, pady=(4,0))

        # ── Progress ──
        pf = ttk.LabelFrame(left, text="Progress"); pf.pack(fill="x", pady=(0,7))
        self.prog_var = tk.DoubleVar()
        ttk.Progressbar(pf, variable=self.prog_var, maximum=100).pack(fill="x", padx=5, pady=(5,2))
        sr = ttk.Frame(pf); sr.pack(fill="x", padx=5, pady=(0,5))
        self.status_lbl = tk.Label(sr, text="Ready", bg=C["bg"], fg=C["sub"], font=("Segoe UI", 9))
        self.status_lbl.pack(side="left")
        self.speed_lbl  = tk.Label(sr, text="", bg=C["bg"], fg=C["teal"], font=("Segoe UI", 9, "bold"))
        self.speed_lbl.pack(side="right")

        # ── Buttons ──
        br = ttk.Frame(left); br.pack(fill="x", pady=(0,6))
        self.dl_btn = ttk.Button(br, text="⬇  Download", style="Green.TButton",
                                  command=self._start_download)
        self.dl_btn.pack(side="left", ipady=5, ipadx=8, padx=(0,5))
        self.cancel_btn = ttk.Button(br, text="⏹ Cancel", style="Red.TButton",
                                      command=self._cancel_download, state="disabled")
        self.cancel_btn.pack(side="left", ipady=5, padx=(0,5))
        ttk.Button(br, text="➕ Add to Queue",
                   command=self._add_to_queue_from_dl).pack(side="left", ipady=5)

        # ── Log ──
        lf = ttk.LabelFrame(left, text="Log"); lf.pack(fill="both", expand=True)
        self.log = tk.Text(lf, height=7, bg=C["surface"], fg=C["green"],
                           font=("Consolas", 8), wrap="word", state="disabled", borderwidth=0)
        self.log.pack(fill="both", expand=True, padx=4, pady=4)
        sb = ttk.Scrollbar(self.log, command=self.log.yview); sb.pack(side="right", fill="y")
        self.log["yscrollcommand"] = sb.set

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — QUEUE
    # ══════════════════════════════════════════════════════════════════════════
    def _tab_queue(self):
        t = self.t_q

        af = ttk.LabelFrame(t, text="Add URL to Queue"); af.pack(fill="x", padx=10, pady=10)
        ar = ttk.Frame(af); ar.pack(fill="x", padx=5, pady=5)
        self.q_url_var = tk.StringVar()
        ttk.Entry(ar, textvariable=self.q_url_var).pack(side="left", fill="x", expand=True)
        ttk.Button(ar, text="Add",          command=self._queue_add_direct).pack(side="left", padx=4)
        ttk.Button(ar, text="📋 Paste & Add",
                   command=self._queue_paste_add).pack(side="left")

        lf = ttk.LabelFrame(t, text="Queue"); lf.pack(fill="both", expand=True, padx=10, pady=(0,10))
        cols = ("URL", "Status", "Format")
        self.q_tree = ttk.Treeview(lf, columns=cols, show="headings", height=12)
        for c in cols: self.q_tree.heading(c, text=c)
        self.q_tree.column("URL", width=380); self.q_tree.column("Status", width=110); self.q_tree.column("Format", width=110)
        qs = ttk.Scrollbar(lf, command=self.q_tree.yview)
        self.q_tree.configure(yscrollcommand=qs.set)
        self.q_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        qs.pack(side="right", fill="y")

        br = ttk.Frame(t); br.pack(fill="x", padx=10, pady=(0,10))
        ttk.Button(br, text="▶ Start All", style="Green.TButton",
                   command=lambda: threading.Thread(target=self._run_queue, daemon=True).start()
                   ).pack(side="left", ipady=5, padx=(0,5))
        ttk.Button(br, text="🗑 Remove Selected", command=self._queue_remove).pack(side="left", padx=(0,5), ipady=5)
        ttk.Button(br, text="✖ Clear All", style="Red.TButton",
                   command=self._queue_clear).pack(side="left", ipady=5)
        self.q_count_lbl = tk.Label(br, text="0 items", bg=C["bg"], fg=C["sub"], font=("Segoe UI", 9))
        self.q_count_lbl.pack(side="right")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — GEO-BYPASS
    # ══════════════════════════════════════════════════════════════════════════
    def _tab_geo(self):
        t = self.t_geo

        tk.Label(t, text="  🌍  Route downloads through a proxy or Tor to bypass geo-restrictions.",
                 bg=C["bg"], fg=C["yellow"], font=("Segoe UI", 10),
                 anchor="w").pack(fill="x", padx=10, pady=(8,0))

        # ── Tor ──
        tf = ttk.LabelFrame(t, text="🧅 Tor Network (Free — no install needed if Tor Browser is open)")
        tf.pack(fill="x", padx=10, pady=10)
        tr = ttk.Frame(tf); tr.pack(fill="x", padx=5, pady=5)
        self.tor_lbl = tk.Label(tr, text="⚪  Tor: Not Active", bg=C["bg"],
                                 fg=C["sub"], font=("Segoe UI", 10, "bold"))
        self.tor_lbl.pack(side="left")
        ttk.Button(tr, text="▶ Connect",    style="Green.TButton", command=self._tor_connect).pack(side="left", padx=5)
        ttk.Button(tr, text="⏹ Disconnect", style="Red.TButton",   command=self._tor_disconnect).pack(side="left", padx=(0,5))
        ttk.Button(tr, text="🔄 New IP",     command=self._tor_newnym).pack(side="left")
        ttk.Button(tr, text="📦 How to Install Tor", command=self._tor_install_guide).pack(side="right", padx=5)
        tk.Label(tf, text="  Tor Browser → port 9150 (auto-detected) | Tor Service → port 9050",
                 bg=C["bg"], fg=C["sub"], font=("Segoe UI", 8)).pack(anchor="w", padx=5, pady=(0,5))

        # ── Free Proxy ──
        pf = ttk.LabelFrame(t, text="🔗 Free Proxy Auto-Fetch  (powered by Geonode API)")
        pf.pack(fill="both", expand=True, padx=10, pady=(0,10))

        cr = ttk.Frame(pf); cr.pack(fill="x", padx=5, pady=5)
        ttk.Label(cr, text="Country:").pack(side="left")
        self.p_country = tk.StringVar(value="Any")
        ttk.Combobox(cr, textvariable=self.p_country, width=7, state="readonly",
                     values=["Any","US","GB","DE","FR","NL","JP","SG","CA","AU","IN","BR"]
                     ).pack(side="left", padx=4)
        ttk.Label(cr, text="Protocol:").pack(side="left")
        self.p_proto = tk.StringVar(value="socks5")
        ttk.Combobox(cr, textvariable=self.p_proto, width=8, state="readonly",
                     values=["http","https","socks4","socks5"]).pack(side="left", padx=4)
        ttk.Button(cr, text="🔄 Fetch Proxies",
                   command=lambda: threading.Thread(target=self._fetch_proxies, daemon=True).start()
                   ).pack(side="left", padx=8)
        ttk.Button(cr, text="⚡ Test All",
                   command=lambda: threading.Thread(target=self._test_proxies, daemon=True).start()
                   ).pack(side="left")
        self.p_status = tk.Label(cr, text="", bg=C["bg"], fg=C["sub"], font=("Segoe UI", 9))
        self.p_status.pack(side="right", padx=5)

        cols = ("IP : Port", "Country", "Protocol", "Ping", "Status")
        self.p_tree = ttk.Treeview(pf, columns=cols, show="headings", height=7)
        for c in cols: self.p_tree.heading(c, text=c)
        self.p_tree.column("IP : Port", width=160); self.p_tree.column("Country", width=70)
        self.p_tree.column("Protocol",  width=75);  self.p_tree.column("Ping",    width=70)
        self.p_tree.column("Status",    width=90)
        ps = ttk.Scrollbar(pf, command=self.p_tree.yview)
        self.p_tree.configure(yscrollcommand=ps.set)
        self.p_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        ps.pack(side="right", fill="y", pady=5)
        self.p_tree.bind("<Double-1>", self._proxy_use_selected)

        ur = ttk.Frame(pf); ur.pack(fill="x", padx=5, pady=(0,5))
        ttk.Button(ur, text="✅ Use Selected", style="Green.TButton",
                   command=self._proxy_use_selected).pack(side="left", padx=(0,5))
        ttk.Button(ur, text="✖ Clear Proxy",   style="Red.TButton",
                   command=self._proxy_clear).pack(side="left")
        self.active_lbl = tk.Label(ur, text="Active Proxy: None", bg=C["bg"],
                                    fg=C["sub"], font=("Segoe UI", 9))
        self.active_lbl.pack(side="right", padx=5)

        # ── Manual proxy ──
        mf = ttk.LabelFrame(t, text="Manual Proxy  (paste any SOCKS5 / HTTP proxy)")
        mf.pack(fill="x", padx=10, pady=(0,10))
        mr = ttk.Frame(mf); mr.pack(fill="x", padx=5, pady=5)
        self.manual_proxy = tk.StringVar()
        ttk.Entry(mr, textvariable=self.manual_proxy, width=40).pack(side="left", padx=(0,5))
        tk.Label(mr, text="e.g.  socks5://1.2.3.4:1080", bg=C["bg"],
                 fg=C["sub"], font=("Segoe UI", 8)).pack(side="left")
        ttk.Button(mr, text="Apply", command=self._proxy_apply_manual).pack(side="right", padx=5)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — HISTORY
    # ══════════════════════════════════════════════════════════════════════════
    def _tab_history(self):
        t = self.t_hist
        cols = ("Time", "Title / URL", "Status")
        self.h_tree = ttk.Treeview(t, columns=cols, show="headings")
        for c in cols: self.h_tree.heading(c, text=c)
        self.h_tree.column("Time", width=130); self.h_tree.column("Title / URL", width=460); self.h_tree.column("Status", width=90)
        hs = ttk.Scrollbar(t, command=self.h_tree.yview)
        self.h_tree.configure(yscrollcommand=hs.set)
        self.h_tree.pack(side="left", fill="both", expand=True, padx=(10,0), pady=10)
        hs.pack(side="right", fill="y", pady=10, padx=(0,10))
        br = ttk.Frame(t); br.pack(fill="x", padx=10, pady=(0,10))
        ttk.Button(br, text="🔄 Refresh",         command=self._hist_refresh).pack(side="left", padx=(0,5), ipady=4)
        ttk.Button(br, text="↩ Re-Download",      command=self._hist_redownload).pack(side="left", padx=(0,5), ipady=4)
        ttk.Button(br, text="🗑 Clear History", style="Red.TButton",
                   command=self._hist_clear).pack(side="left", ipady=4)
        self._hist_refresh()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 5 — SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    def _tab_settings(self):
        t = self.t_set

        gf = ttk.LabelFrame(t, text="General"); gf.pack(fill="x", padx=10, pady=10)
        gi = ttk.Frame(gf); gi.pack(fill="x", padx=5, pady=5)

        self.s_folder   = tk.StringVar(value=self.settings["save_folder"])
        self.s_tmpl     = tk.StringVar(value=self.settings["filename_template"])
        self.s_frags    = tk.StringVar(value=self.settings["fragments"])
        self.s_cookie   = tk.StringVar(value=self.settings["cookie_file"])
        self.s_limit    = tk.StringVar(value=self.settings["speed_limit"])

        rows = [
            ("Default Folder",       self.s_folder,  "folder"),
            ("Filename Template",    self.s_tmpl,    None),
            ("Concurrent Fragments", self.s_frags,   "spin"),
            ("Cookie File (.txt)",   self.s_cookie,  "file"),
            ("Speed Limit (KB/s)",   self.s_limit,   "spin2"),
        ]
        for i, (lbl, var, kind) in enumerate(rows):
            ttk.Label(gi, text=lbl+":").grid(row=i, column=0, sticky="w", pady=3, padx=(0,6))
            if kind == "spin":
                ttk.Spinbox(gi, from_=1, to=16, textvariable=var, width=6).grid(row=i, column=1, sticky="w", padx=4)
                ttk.Label(gi, text="(1–16)", foreground=C["sub"]).grid(row=i, column=2, sticky="w")
            elif kind == "spin2":
                ttk.Spinbox(gi, from_=0, to=100000, textvariable=var, width=8).grid(row=i, column=1, sticky="w", padx=4)
                ttk.Label(gi, text="0 = unlimited", foreground=C["sub"]).grid(row=i, column=2, sticky="w")
            elif kind == "folder":
                ttk.Entry(gi, textvariable=var, width=38).grid(row=i, column=1, padx=4)
                ttk.Button(gi, text="📁",
                           command=lambda v=var: v.set(filedialog.askdirectory() or v.get())
                           ).grid(row=i, column=2)
            elif kind == "file":
                ttk.Entry(gi, textvariable=var, width=38).grid(row=i, column=1, padx=4)
                ttk.Button(gi, text="📁",
                           command=lambda v=var: v.set(
                               filedialog.askopenfilename(filetypes=[("Text","*.txt"),("All","*.*")]) or v.get())
                           ).grid(row=i, column=2)
            else:
                ttk.Entry(gi, textvariable=var, width=38).grid(row=i, column=1, padx=4)

        tf2 = ttk.LabelFrame(t, text="Maintenance"); tf2.pack(fill="x", padx=10, pady=(0,10))
        tr2 = ttk.Frame(tf2); tr2.pack(fill="x", padx=5, pady=5)
        ttk.Button(tr2, text="⬆ Update yt-dlp",
                   command=lambda: threading.Thread(target=self._update_ytdlp, daemon=True).start()
                   ).pack(side="left", ipady=4, padx=(0,5))
        ttk.Button(tr2, text="📦 Check ffmpeg",
                   command=self._check_ffmpeg).pack(side="left", ipady=4, padx=(0,5))
        ttk.Button(tr2, text="💾 Save Settings", style="Green.TButton",
                   command=self._save_settings_action).pack(side="right", ipady=4)
        self.maint_log = tk.Text(tf2, height=4, bg=C["surface"], fg=C["green"],
                                  font=("Consolas", 8), state="disabled", borderwidth=0)
        self.maint_log.pack(fill="x", padx=5, pady=(0,5))

    # ══════════════════════════════════════════════════════════════════════════
    # DOWNLOAD LOGIC
    # ══════════════════════════════════════════════════════════════════════════
    def _build_cmd(self, url):
        if not url: raise ValueError("Please enter a URL.")
        fmt    = self.fmt_var.get()
        qual   = self.qual_var.get()
        height = QUALITY_MAP.get(qual)
        frags  = self.settings.get("fragments", "5")

        cmd = ["yt-dlp"]

        if fmt == "Best MP4":
            if height:
                cmd += ["-f", f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={height}]+bestaudio/best"]
            else:
                cmd += ["-S", "ext:mp4:m4a"]
            cmd += ["--merge-output-format", "mp4"]
        elif fmt == "Best Quality":
            if height:
                cmd += ["-f", f"bestvideo[height<={height}]+bestaudio/best"]
        elif fmt == "Audio Only (MP3)":
            cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0"]
        elif fmt == "Audio Only (M4A)":
            cmd += ["-x", "--audio-format", "m4a"]
        elif fmt == "Video Only":
            cmd += ["-f", "bestvideo"]
        elif fmt == "WebM":
            cmd += ["-f", "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]"]

        if self.emb_thumb.get(): cmd += ["--embed-thumbnail"]
        if self.emb_subs.get():  cmd += ["--embed-subs", "--sub-lang", self.sub_lang.get()]

        cmd += ["-P", self.folder_var.get()]
        cmd += ["-o", self.fname_var.get()]
        cmd += ["--concurrent-fragments", frags]

        ck = self.settings.get("cookie_file", "")
        if ck and os.path.exists(ck): cmd += ["--cookies", ck]

        try:
            lim = int(self.settings.get("speed_limit", "0"))
            if lim > 0: cmd += ["-r", f"{lim}K"]
        except Exception: pass

        if self.active_proxy: cmd += ["--proxy", self.active_proxy]

        cmd.append(url)
        return cmd

    def _start_download(self, url=None):
        if self.is_downloading:
            messagebox.showwarning("Busy", "Already downloading! Add to queue instead."); return
        threading.Thread(target=self._run_download, args=(url,), daemon=True).start()

    def _run_download(self, url=None):
        self.is_downloading = True
        self.dl_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.prog_var.set(0)
        url_ = url or self.url_var.get().strip()

        try:
            cmd = self._build_cmd(url_)
            self._log(f"▶ {url_}\n")
            self._status("Downloading…", C["blue"])
            self.download_process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace")

            dest = url_
            for line in self.download_process.stdout:
                line = line.strip()
                if line:
                    self._log(line)
                    self._parse_progress(line)
                    if "Destination:" in line:
                        dest = line.split("Destination:")[-1].strip()

            self.download_process.wait()
            rc = self.download_process.returncode
            if rc == 0:
                self._status("✅ Complete!", C["green"])
                self._log("\n✅ Done!\n")
                self.prog_var.set(100)
                self.add_history(url_, dest, "✅ Done")
            else:
                self._status("❌ Failed", C["red"])
                self._log(f"\n❌ Failed (exit {rc})\n")
                self.add_history(url_, url_, "❌ Failed")
            self._hist_refresh()

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except FileNotFoundError:
            messagebox.showerror("yt-dlp missing", "Run:  pip install yt-dlp")
        finally:
            self.is_downloading = False
            self.dl_btn.configure(state="normal")
            self.cancel_btn.configure(state="disabled")
            self.speed_lbl.configure(text="")

    def _cancel_download(self):
        if self.download_process:
            self.download_process.terminate()
            self._log("\n⏹ Cancelled.\n")
            self._status("Cancelled", C["yellow"])

    def _parse_progress(self, line):
        if "[download]" in line and "%" in line:
            try:
                m = re.search(r"(\d+\.?\d*)%", line)
                sp = re.search(r"at\s+([\d.]+\s*\S+/s)", line)
                eta = re.search(r"ETA\s+(\S+)", line)
                if m: self.prog_var.set(float(m.group(1)))
                parts = []
                if sp:  parts.append(f"⚡ {sp.group(1)}")
                if eta: parts.append(f"ETA {eta.group(1)}")
                if parts: self.speed_lbl.configure(text="  ".join(parts))
            except Exception: pass

    def _fetch_info(self):
        url = self.url_var.get().strip()
        if not url: return
        try:
            r = subprocess.run(
                ["yt-dlp", "--dump-json", "--no-playlist", url] +
                (["--proxy", self.active_proxy] if self.active_proxy else []),
                capture_output=True, text=True, timeout=30)
            if r.returncode == 0:
                info = json.loads(r.stdout)
                txt = (f"{info.get('title','?')}\n\n"
                       f"Duration : {info.get('duration_string','?')}\n"
                       f"Uploader : {info.get('uploader','?')}\n"
                       f"Views    : {info.get('view_count',0):,}\n"
                       f"Likes    : {info.get('like_count',0):,}")
                self.info_box.configure(state="normal")
                self.info_box.delete("1.0", "end")
                self.info_box.insert("1.0", txt)
                self.info_box.configure(state="disabled")
                thumb = info.get("thumbnail")
                if thumb and HAS_PIL: self._load_thumb(thumb)
        except Exception: pass

    def _load_thumb(self, url):
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                data = r.read()
            img = Image.open(io.BytesIO(data)).resize((166, 94), Image.LANCZOS)
            ph = ImageTk.PhotoImage(img)
            self.thumb_lbl.configure(image=ph, text="")
            self.thumb_lbl.image = ph
        except Exception: pass

    def _log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _status(self, text, color):
        self.status_lbl.configure(text=text, fg=color)

    def _browse_folder(self):
        d = filedialog.askdirectory()
        if d: self.folder_var.set(d)

    # ══════════════════════════════════════════════════════════════════════════
    # QUEUE LOGIC
    # ══════════════════════════════════════════════════════════════════════════
    def _queue_add(self, url, fmt):
        if not url: return
        self.q_tree.insert("", "end", values=(url, "Pending", fmt))
        self.q_count_lbl.configure(text=f"{len(self.q_tree.get_children())} items")

    def _add_to_queue_from_dl(self):
        self._queue_add(self.url_var.get().strip(), self.fmt_var.get())
        self.nb.select(self.t_q)

    def _queue_add_direct(self):
        self._queue_add(self.q_url_var.get().strip(), self.fmt_var.get())
        self.q_url_var.set("")

    def _queue_paste_add(self):
        self.q_url_var.set(self.root.clipboard_get())
        self._queue_add_direct()

    def _queue_remove(self):
        for i in self.q_tree.selection(): self.q_tree.delete(i)
        self.q_count_lbl.configure(text=f"{len(self.q_tree.get_children())} items")

    def _queue_clear(self):
        for i in self.q_tree.get_children(): self.q_tree.delete(i)
        self.q_count_lbl.configure(text="0 items")

    def _run_queue(self):
        for item in self.q_tree.get_children():
            url = self.q_tree.item(item)["values"][0]
            self.q_tree.set(item, "Status", "⬇ Downloading…")
            try:
                cmd = self._build_cmd(url)
                r = subprocess.run(cmd, capture_output=True, text=True)
                self.q_tree.set(item, "Status", "✅ Done" if r.returncode == 0 else "❌ Failed")
                self.add_history(url, url, "✅ Done" if r.returncode == 0 else "❌ Failed")
            except Exception as e:
                self.q_tree.set(item, "Status", f"❌ {e}")
        self._hist_refresh()

    # ══════════════════════════════════════════════════════════════════════════
    # GEO-BYPASS LOGIC
    # ══════════════════════════════════════════════════════════════════════════
    def _tor_connect(self):
        for port in [9150, 9050]:   # Tor Browser first, then Tor service
            try:
                s = socket.socket(); s.settimeout(3)
                if s.connect_ex(("127.0.0.1", port)) == 0:
                    s.close()
                    self.active_proxy = f"socks5://127.0.0.1:{port}"
                    self.tor_active = True
                    label = "Tor Browser" if port == 9150 else "Tor Service"
                    self.tor_lbl.configure(text=f"🟢  {label} Active (:{port})", fg=C["green"])
                    self.proxy_badge.configure(text=f"🟢  Tor :{port}", fg=C["green"])
                    self._update_active_lbl()
                    return
                s.close()
            except Exception: pass
        messagebox.showwarning("Tor Not Found",
            "Tor not detected on ports 9150 or 9050.\n\n"
            "Fix:\n"
            "  1.  Open Tor Browser  (auto-detects port 9150)\n"
            "  2.  OR run:  winget install TorProject.TorBrowser")

    def _tor_disconnect(self):
        if self.tor_active:
            self.active_proxy = ""
            self.tor_active   = False
        self.tor_lbl.configure(text="⚪  Tor: Not Active", fg=C["sub"])
        self.proxy_badge.configure(text="⚪  No Proxy", fg=C["sub"])
        self._update_active_lbl()

    def _tor_newnym(self):
        try:
            s = socket.socket(); s.connect(("127.0.0.1", 9051)); s.settimeout(5)
            s.sendall(b'AUTHENTICATE ""\r\nSIGNAL NEWNYM\r\nQUIT\r\n')
            s.close()
            self.tor_lbl.configure(text="🟢  Tor: New Identity Requested!", fg=C["teal"])
        except Exception:
            messagebox.showinfo("Tor", "New identity failed — Tor control port (9051) not reachable.")

    def _tor_install_guide(self):
        messagebox.showinfo("Install Tor",
            "Windows (easiest):\n\n"
            "  winget install TorProject.TorBrowser\n\n"
            "After install → open Tor Browser → click Connect\n"
            "Then click ▶ Connect here (port 9150 auto-detected).\n\n"
            "For headless (no browser):\n"
            "  winget install TorProject.Tor\n"
            "  tor   ← run this in a terminal first\n"
            "  Then click ▶ Connect here (port 9050).")

    def _fetch_proxies(self):
        self.p_status.configure(text="Fetching…", fg=C["yellow"])
        for i in self.p_tree.get_children(): self.p_tree.delete(i)
        try:
            country = self.p_country.get()
            proto   = self.p_proto.get()
            cp = f"&country={country}" if country != "Any" else ""
            url = (f"https://proxylist.geonode.com/api/proxy-list"
                   f"?limit=80&page=1&sort_by=speed&sort_type=asc&protocols={proto}{cp}")
            req = urllib.request.Request(url, headers={
                "User-Agent":  "Mozilla/5.0",
                "Accept":      "application/json",
                "Origin":      "https://geonode.com"})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())
            proxies = data.get("data", [])
            for p in proxies:
                ip    = p.get("ip", "")
                port  = p.get("port", "")
                c_    = p.get("country", "?")
                proto_= (p.get("protocols") or [proto])[0].upper()
                spd   = p.get("speed") or p.get("responseTime") or "?"
                self.p_tree.insert("", "end",
                    values=(f"{ip}:{port}", c_, proto_, f"{spd}ms", "Untested"))
            self.p_status.configure(text=f"✅ {len(proxies)} proxies", fg=C["green"])
        except Exception as e:
            self.p_status.configure(text=f"❌ {str(e)[:45]}", fg=C["red"])

    def _test_proxies(self):
        items = self.p_tree.get_children()
        self.p_status.configure(text="Testing…", fg=C["yellow"])
        live = 0

        for item in items:
            vals  = self.p_tree.item(item)["values"]
            addr  = vals[0]
            proto = vals[2].lower()

            # Normalize protocol
            if proto in ("http", "https"):
                proxy_url = f"http://{addr}"
            elif proto == "socks4":
                proxy_url = f"socks4://{addr}"
            else:
                proxy_url = f"socks5://{addr}"

            try:
                ip, port_s = addr.rsplit(":", 1)
                t0  = time.time()
                # Step 1: TCP check
                s = socket.socket(); s.settimeout(4)
                ok  = s.connect_ex((ip, int(port_s))) == 0
                s.close()
                ms  = int((time.time() - t0) * 1000)

                if ok:
                    # Step 2: Real HTTP test through the proxy
                    try:
                        req = urllib.request.Request(
                            "http://httpbin.org/ip",
                            headers={"User-Agent": "Mozilla/5.0"})

                        # For HTTP proxies, set env-style proxy
                        proxy_handler = urllib.request.ProxyHandler(
                            {"http": proxy_url, "https": proxy_url})
                        opener = urllib.request.build_opener(proxy_handler)
                        with opener.open(req, timeout=6) as r:
                            body = r.read().decode()
                        if '"origin"' in body:
                            self.p_tree.set(item, "Ping",   f"{ms}ms")
                            self.p_tree.set(item, "Status", "✅ Working")
                            live += 1
                        else:
                            self.p_tree.set(item, "Status", "⚠ TCP ok/blocked")
                    except Exception:
                        self.p_tree.set(item, "Ping",   f"{ms}ms")
                        self.p_tree.set(item, "Status", "⚠ TCP ok/no HTTP")
                else:
                    self.p_tree.set(item, "Status", "❌ Offline")

            except Exception:
                self.p_tree.set(item, "Status", "❌ Error")

        self.p_status.configure(text=f"Done — {live} fully working", fg=C["green"])

    def _proxy_use_selected(self, _event=None):
        sel = self.p_tree.selection()
        if not sel: return
        vals  = self.p_tree.item(sel[0])["values"]
        addr  = vals[0]
        proto = vals[2].lower()

        # ✅ yt-dlp only accepts http://, socks4://, socks5://
        if proto in ("http", "https"):
            proxy_str = f"http://{addr}"
        elif proto == "socks4":
            proxy_str = f"socks4://{addr}"
        else:
            proxy_str = f"socks5://{addr}"   # socks5 default

        self.active_proxy = proxy_str
        self._update_active_lbl()
        self.proxy_badge.configure(text=f"🟢  {addr}", fg=C["green"])

    def _proxy_apply_manual(self):
        p = self.manual_proxy.get().strip()
        if not p:
            return
        # Auto-fix bare IP:port → assume http
        if p and not p.startswith(("http://","socks4://","socks5://")):
            p = f"http://{p}"
        self.active_proxy = p
        self._update_active_lbl()
        self.proxy_badge.configure(text=f"🟢  {p.split('//')[-1]}", fg=C["green"])

    def _proxy_clear(self):
        self.active_proxy = ""
        self.tor_active   = False
        self._update_active_lbl()
        self.proxy_badge.configure(text="⚪  No Proxy", fg=C["sub"])
        self.tor_lbl.configure(text="⚪  Tor: Not Active", fg=C["sub"])

    def _update_active_lbl(self):
        self.active_lbl.configure(
            text=f"Active Proxy: {self.active_proxy or 'None'}",
            fg=C["green"] if self.active_proxy else C["sub"])

    # ══════════════════════════════════════════════════════════════════════════
    # HISTORY LOGIC
    # ══════════════════════════════════════════════════════════════════════════
    def _hist_refresh(self):
        for i in self.h_tree.get_children(): self.h_tree.delete(i)
        for e in reversed(self.history[-100:]):
            self.h_tree.insert("", "end",
                values=(e.get("time",""), e.get("title", e.get("url","")), e.get("status","")))

    def _hist_redownload(self):
        sel = self.h_tree.selection()
        if not sel: return
        url = self.h_tree.item(sel[0])["values"][1]
        self.url_var.set(url)
        self.nb.select(self.t_dl)

    def _hist_clear(self):
        if messagebox.askyesno("Clear History", "Delete all download history?"):
            self.history.clear()
            if os.path.exists(HISTORY_FILE): os.remove(HISTORY_FILE)
            self._hist_refresh()

    # ══════════════════════════════════════════════════════════════════════════
    # SETTINGS LOGIC
    # ══════════════════════════════════════════════════════════════════════════
    def _save_settings_action(self):
        self.settings.update({
            "save_folder":       self.s_folder.get(),
            "filename_template": self.s_tmpl.get(),
            "fragments":         self.s_frags.get(),
            "cookie_file":       self.s_cookie.get(),
            "speed_limit":       self.s_limit.get(),
        })
        self.folder_var.set(self.settings["save_folder"])
        self.fname_var.set(self.settings["filename_template"])
        self.save_settings()
        self._mlog("✅ Settings saved.\n")

    def _update_ytdlp(self):
        self._mlog("Updating yt-dlp…\n")
        r = subprocess.run(["pip", "install", "--upgrade", "yt-dlp"],
                           capture_output=True, text=True)
        self._mlog((r.stdout or r.stderr or "Done.").strip() + "\n")

    def _check_ffmpeg(self):
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if r.returncode == 0:
            self._mlog("✅ ffmpeg: " + r.stdout.split("\n")[0] + "\n")
        else:
            self._mlog("❌ ffmpeg not found.\nFix: winget install ffmpeg\n")

    def _mlog(self, text):
        self.maint_log.configure(state="normal")
        self.maint_log.insert("end", text)
        self.maint_log.see("end")
        self.maint_log.configure(state="disabled")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    YtDlpPro(root)
    root.mainloop()