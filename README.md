# yt-dlp GUI

A lightweight desktop GUI for **yt-dlp** built with **Python** and **PySide6**. It provides a simple interface for downloading videos, playlists, audio, subtitles, and metadata without using the command line.

## Features

- Download videos from YouTube and hundreds of supported websites
- Download playlists
- Audio-only mode
- Select video quality
- Custom output directory
- Download subtitles
- View download logs
- Simple and clean interface
- Cross-platform (Windows, Linux)

---

## Screenshots

> Add screenshots here.

---

## Requirements

- Python 3.10 or newer
- FFmpeg (recommended)
- Internet connection

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/adityaksx/yt-dlp-gui.git
cd yt-dlp-gui
```

### 2. Create a virtual environment (Recommended)

Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you don't have a requirements file yet:

```bash
pip install PySide6 yt-dlp requests
```

If your project uses additional libraries, install them as well.

---

## Install FFmpeg

FFmpeg is recommended for:

- Merging audio and video
- Audio extraction
- Higher quality downloads
- Format conversion

### Windows

Using Winget

```powershell
winget install Gyan.FFmpeg
```

Or download manually from:

https://ffmpeg.org/download.html

Make sure FFmpeg is added to your PATH.

---

## Running the Application

If your main file is:

```text
main.py
```

Run:

```bash
python main.py
```

If your entry point is different:

```bash
python app.py
```

or

```bash
python gui.py
```

Replace the filename accordingly.

---

## Project Structure

```
yt-dlp-gui/
│
├── assets/
├── ui/
├── downloads/
├── main.py
├── requirements.txt
├── README.md
└── LICENSE
```

---

## Building an Executable

Install PyInstaller

```bash
pip install pyinstaller
```

Build

```bash
pyinstaller --onefile --windowed main.py
```

Executable will be inside:

```
dist/
```

---

## Dependencies

- PySide6
- yt-dlp
- requests
- FFmpeg (external)

---

## Updating yt-dlp

```bash
pip install -U yt-dlp
```

---

## Contributing

Pull requests are welcome.

For major changes, please open an issue first.

---

## License

MIT License

---

## Credits

- yt-dlp
- PySide6
- FFmpeg
