# yt-dlp GUI

*[Read in French / Lire en Français](README.fr.md)*

A modern, feature-rich graphical interface for [yt-dlp](https://github.com/yt-dlp/yt-dlp), built with Python and CustomTkinter.

![Screenshot](src/assets/icon.png)

## Features

-   **Modern UI**: Clean, dark-themed interface using CustomTkinter.
-   **Format Selection**: Choose between Video+Audio or Audio Only.
-   **Quality Control**: Select video quality (Best, 1080p, 720p, etc.).
-   **Queue System**: Queue multiple downloads and process them concurrently.
-   **Preview**: Automatically fetches and displays video metadata (thumbnail, title, duration) before downloading.
-   **Smart Naming**: Customizable output filename patterns.
-   **Cookies Support**: Import cookies from your browser for premium/age-restricted content.
-   **Embedded Metadata**: thorough metadata tagging and thumbnail embedding.

## Installation

### Pre-built Executable (Windows)
1.  Download the latest release from the [Releases](https://github.com/yourusername/yt-dlp-gui/releases) page.
2.  Extract the zip file.
3.  Run `yt-dlp-gui.exe`.

### Running from Source
1.  **Prerequisites**: Python 3.8+
2.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/yt-dlp-gui.git
    cd yt-dlp-gui
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the application**:
    ```bash
    python main.py
    ```

## Usage

1.  **Paste URL**: Paste a YouTube (or other supported site) link into the input field.
2.  **Preview**: The app will automatically fetch and show a preview of the video.
3.  **Configure**: Select your desired format and quality options.
4.  **Download**: Click "Confirm Download" or the main "Download" button to add it to the queue.
5.  **Manage**: Monitor progress, cancel, or retry downloads from the list.


## ⚙️ Configuration & Parameters

The application offers several settings to customize your download experience. Click the **Settings (⚙)** button to access them:

### 1. General Settings
-   **Download Path**: The folder where downloaded files will be saved. Default is your system's `Downloads` folder.
-   **Theme**: Choose between "Dark" (default) or "Light" mode.
-   **Temporary Directory**: Location for intermediate files (useful if you have limited space on C:).

### 2. Output Formatting (Naming Pattern)
Customize how your files are named using `yt-dlp` output templates.
-   **Default Pattern**: `%(upload_date>%Y.%m.%d)s.%(title)s [%(id)s].%(ext)s`
    -   Example result: `2023.12.31.My Video Title [dQw4w9WgXcQ].mp4`
-   **Common Variables**:
    -   `%(title)s`: Video title.
    -   `%(id)s`: Video ID.
    -   `%(uploader)s`: Channel name.
    -   `%(upload_date)s`: Date (YYYYMMDD).
-   **📚 Documentation**: For a full list of available variables, refer to the [yt-dlp Output Template Documentation](https://github.com/yt-dlp/yt-dlp#output-template).

### 3. Authentication (Cookies)
Required for downloading:
-   **Premium content** (YouTube Premium).
-   **Age-restricted videos**.
-   **Members-only videos**.

**How to use**:
Provide a path to a `cookies.txt` file (exported using browser extensions like "Get cookies.txt").

### 4. Advanced (Binaries)
The application attempts to automatically detect `yt-dlp` and `ffmpeg`.
-   **yt-dlp Path**: Manually specify the path to `yt-dlp.exe` if the embedded version is outdated or failing.
-   **FFmpeg Path**: Manually specify `ffmpeg.exe`. **FFmpeg is required** to merge video and audio streams for high-quality downloads (1080p+).

---

## 📦 Dependencies & Installation

### Python Dependencies
The application relies on several Python libraries, listed in `requirements.txt`:
-   `customtkinter`: For the modern GUI.
-   `yt-dlp`: The core downloading engine.
-   `pillow`: For image processing (thumbnails).
-   `packaging`: For version comparison.

To install them:
```bash
pip install -r requirements.txt
```

### External Tools (FFmpeg & Deno)
For full functionality, the following external tools are highly recommended:

1.  **FFmpeg**: Required to merge high-quality video and audio streams (1080p+).
    -   Download from [ffmpeg.org](https://ffmpeg.org/download.html).
    -   Add to system PATH or specify in Settings.

2.  **Deno**: Required by `yt-dlp` for some sites (like YouTube) to bypass diverse protections.
    -   Run this command in PowerShell (no Admin rights required): [Source](https://deno.com/)
        ```powershell
        iwr https://deno.land/x/install/install.ps1 -useb | iex
        ```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgements

-   [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the powerful download engine.
-   [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the UI library.
