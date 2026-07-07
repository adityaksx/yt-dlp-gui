## Installation

### 1. Clone the repository

```bash
git clone https://github.com/adityaksx/yt-dlp-gui.git
cd yt-dlp-gui
```

### 2. Install dependencies

If a `requirements.txt` file exists:

```bash
pip install -r requirements.txt
```

Otherwise install the required libraries manually:

```bash
pip install PySide6 yt-dlp requests
```

---

## Install FFmpeg (Recommended)

FFmpeg is required for:

- Merging video and audio
- Extracting audio
- Converting formats
- Downloading the highest available quality

### Windows

Install using Winget:

```powershell
winget install Gyan.FFmpeg
```

Or download it from the official FFmpeg website and add it to your system PATH. :contentReference[oaicite:0]{index=0}

---

## Running the Application

If your main file is `main.py`:

```bash
python main.py
```

If your entry point has a different name, replace `main.py` with the appropriate filename.

Example:

```bash
python app.py
```

or

```bash
python gui.py
```

---

## Required Libraries

- PySide6
- yt-dlp
- requests

Install them with:

```bash
pip install PySide6 yt-dlp requests
```

---

## Update yt-dlp

```bash
pip install -U yt-dlp
```
