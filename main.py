import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import os

class YtDlpGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("yt-dlp Downloader")
        self.root.geometry("650x520")
        self.root.configure(bg="#1e1e2e")
        self.build_ui()

    def build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#1e1e2e", foreground="#cdd6f4", font=("Segoe UI", 10))
        style.configure("TEntry", fieldbackground="#313244", foreground="#cdd6f4", font=("Segoe UI", 10))
        style.configure("TButton", background="#89b4fa", foreground="#1e1e2e", font=("Segoe UI", 10, "bold"))
        style.configure("TCombobox", fieldbackground="#313244", foreground="#cdd6f4")

        pad = {"padx": 10, "pady": 5}

        # URL
        ttk.Label(self.root, text="Video URL:").grid(row=0, column=0, sticky="w", **pad)
        self.url_var = tk.StringVar()
        ttk.Entry(self.root, textvariable=self.url_var, width=55).grid(row=0, column=1, columnspan=2, **pad)

        # Format
        ttk.Label(self.root, text="Format:").grid(row=1, column=0, sticky="w", **pad)
        self.format_var = tk.StringVar(value="Best MP4")
        formats = ["Best MP4", "Best Quality", "Audio Only (MP3)", "720p", "480p", "360p"]
        ttk.Combobox(self.root, textvariable=self.format_var, values=formats, width=20, state="readonly").grid(row=1, column=1, sticky="w", **pad)

        # Output folder
        ttk.Label(self.root, text="Save to:").grid(row=2, column=0, sticky="w", **pad)
        self.folder_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        ttk.Entry(self.root, textvariable=self.folder_var, width=42).grid(row=2, column=1, **pad)
        ttk.Button(self.root, text="Browse", command=self.browse_folder).grid(row=2, column=2, **pad)

        # Proxy / VPN
        ttk.Label(self.root, text="Proxy (VPN):").grid(row=3, column=0, sticky="w", **pad)
        self.proxy_var = tk.StringVar(placeholder := "socks5://127.0.0.1:1080  or  http://proxy:port")
        proxy_entry = ttk.Entry(self.root, textvariable=self.proxy_var, width=42)
        proxy_entry.insert(0, "socks5://127.0.0.1:1080  or  http://proxy:port")
        proxy_entry.grid(row=3, column=1, columnspan=2, **pad)
        self.proxy_entry = proxy_entry

        # Concurrent fragments
        ttk.Label(self.root, text="Speed boost:").grid(row=4, column=0, sticky="w", **pad)
        self.frag_var = tk.StringVar(value="5")
        ttk.Spinbox(self.root, from_=1, to=16, textvariable=self.frag_var, width=5).grid(row=4, column=1, sticky="w", **pad)
        ttk.Label(self.root, text="concurrent fragments").grid(row=4, column=1, sticky="w", padx=80)

        # Download button
        ttk.Button(self.root, text="⬇ Download", command=self.start_download).grid(row=5, column=0, columnspan=3, pady=12)

        # Log output
        ttk.Label(self.root, text="Log:").grid(row=6, column=0, sticky="w", **pad)
        self.log = tk.Text(self.root, height=14, bg="#313244", fg="#a6e3a1",
                           font=("Consolas", 9), wrap="word", state="disabled")
        self.log.grid(row=7, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

        scrollbar = ttk.Scrollbar(self.root, command=self.log.yview)
        scrollbar.grid(row=7, column=3, sticky="ns")
        self.log["yscrollcommand"] = scrollbar.set

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def log_write(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def build_command(self):
        url = self.url_var.get().strip()
        if not url:
            raise ValueError("Please enter a URL.")

        fmt = self.format_var.get()
        folder = self.folder_var.get()
        proxy = self.proxy_entry.get().strip()
        frags = self.frag_var.get()

        cmd = ["yt-dlp"]

        format_map = {
            "Best MP4": ["-S", "ext:mp4:m4a", "--merge-output-format", "mp4"],
            "Best Quality": [],
            "Audio Only (MP3)": ["-x", "--audio-format", "mp3"],
            "720p": ["-f", "bestvideo[height<=720]+bestaudio", "--merge-output-format", "mp4"],
            "480p": ["-f", "bestvideo[height<=480]+bestaudio", "--merge-output-format", "mp4"],
            "360p": ["-f", "bestvideo[height<=360]+bestaudio", "--merge-output-format", "mp4"],
        }
        cmd += format_map.get(fmt, [])
        cmd += ["-P", folder]
        cmd += ["-o", "%(title)s.%(ext)s"]
        cmd += ["--concurrent-fragments", frags]

        if proxy and "127.0.0.1" not in proxy and "proxy:port" not in proxy:
            cmd += ["--proxy", proxy]

        cmd.append(url)
        return cmd

    def run_download(self):
        try:
            cmd = self.build_command()
            self.log_write(f"Running: {' '.join(cmd)}\n")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                self.log_write(line.strip())
            process.wait()
            if process.returncode == 0:
                self.log_write("\n✅ Download complete!")
            else:
                self.log_write("\n❌ Error occurred. Check log above.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except FileNotFoundError:
            messagebox.showerror("Error", "yt-dlp not found! Run: pip install yt-dlp")

    def start_download(self):
        threading.Thread(target=self.run_download, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = YtDlpGUI(root)
    root.mainloop()