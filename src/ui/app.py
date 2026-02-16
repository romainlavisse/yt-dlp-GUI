import customtkinter as ctk
import logging
import threading
import re
from src.core.download_manager import DownloadManager
from src.core.queue_manager import event_queue
from src.ui.download_frame import DownloadFrame
from src.ui.settings_dialog import SettingsDialog
from src.ui.components.preview_panel import PreviewPanel
from src.services.ytdlp_wrapper import YtDlpWrapper


logger = logging.getLogger(__name__)

class App(ctk.CTk):
    """
    Main Application Window class.
    
    Layout:
    - 2-column grid layout.
    - Left Column (weight=2): Controls (URL, Settings), Options (Checkboxes, Quality), Download List, Status Bar.
    - Right Column (weight=1): Preview Panel (Thumbnail, Title, Info).
    
    Responsibilities:
    - Initializes the UI components.
    - Manages the main event loop.
    - Handles user interactions (buttons, inputs).
    - Coordinates between the UI and the DownloadManager.
    - Updates UI based on events from the background download threads.
    """
    def __init__(self):
        super().__init__()
        
        # 1. Setup Window Properties
        self.title("yt-dlp GUI")
        self.geometry("1000x650")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # Set window icon (taskbar + title bar)
        self._set_icon()
        
        # 2. Logic Initialization
        self.dm = DownloadManager()
        self.current_url = ""
        self.current_metadata = {}  # Store metadata for title display in download list
        self._url_check_id = None  # Timer ID for debouncing URL paste detection
        
        # 3. Main Layout Configuration: 2 columns
        self.grid_columnconfigure(0, weight=2)  # Left column (main controls)
        self.grid_columnconfigure(1, weight=1)  # Right column (preview)
        self.grid_rowconfigure(2, weight=1)     # Row 2 (Download list) expands to fill detail
        
        # === LEFT COLUMN ===
        
        # Header Frame (URL Input + Settings Button) - Row 0
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Settings Button
        self.btn_settings = ctk.CTkButton(self.header_frame, text="⚙", width=35, command=self.open_settings)
        self.btn_settings.pack(side="left", padx=(5, 5), pady=5)
        
        # URL Input Field
        self.entry_url = ctk.CTkEntry(self.header_frame, placeholder_text="Paste YouTube URL here...")
        self.entry_url.pack(side="left", fill="x", expand=True, padx=(0, 5), pady=5)
        # Bind keys for auto-detection of URLs
        self.entry_url.bind("<KeyRelease>", self._on_url_change)
        self.entry_url.bind("<Control-v>", self._on_url_paste)
        
        # Download Button
        self.btn_download = ctk.CTkButton(self.header_frame, text="Download", command=self.on_download_click)
        self.btn_download.pack(side="right", padx=(0, 5), pady=5)
        
        # Options Container Frame - Row 1
        self.options_container = ctk.CTkFrame(self)
        self.options_container.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        
        # Row 1 inside Options: Checkboxes
        self.options_row1 = ctk.CTkFrame(self.options_container, fg_color="transparent")
        self.options_row1.pack(fill="x", padx=5, pady=(5, 0))
        
        self.chk_download_video = ctk.CTkCheckBox(self.options_row1, text="Download Video", width=20)
        self.chk_download_video.select()
        self.chk_download_video.pack(side="left", padx=(10, 15), pady=3)
        
        self.chk_save_thumb = ctk.CTkCheckBox(self.options_row1, text="Save Thumbnail", width=20)
        self.chk_save_thumb.pack(side="left", padx=15, pady=3)
        
        self.chk_embed_thumb = ctk.CTkCheckBox(self.options_row1, text="Embed Thumbnail", width=20)
        self.chk_embed_thumb.pack(side="left", padx=15, pady=3)
        
        # Row 2 inside Options: Mode + Quality Selectors
        self.options_row2 = ctk.CTkFrame(self.options_container, fg_color="transparent")
        self.options_row2.pack(fill="x", padx=5, pady=(0, 5))
        
        lbl_mode = ctk.CTkLabel(self.options_row2, text="Mode:", font=("Segoe UI", 11))
        lbl_mode.pack(side="left", padx=(10, 5), pady=3)
        
        self.download_mode = ctk.CTkSegmentedButton(
            self.options_row2, 
            values=["Video+Audio", "Audio Only"],
            command=self.on_mode_change
        )
        self.download_mode.set("Video+Audio")
        self.download_mode.pack(side="left", padx=5, pady=3)
        
        lbl_quality = ctk.CTkLabel(self.options_row2, text="Quality:", font=("Segoe UI", 11))
        lbl_quality.pack(side="left", padx=(20, 5), pady=3)
        
        self.combo_quality = ctk.CTkComboBox(
            self.options_row2, width=160,
            values=["Best Quality", "1080p", "720p", "480p", "360p"],
            state="readonly"
        )
        self.combo_quality.set("Best Quality")
        self.combo_quality.pack(side="left", padx=5, pady=3)
        
        # Download List Frame - Row 2
        # Initialize with the configured download path
        download_path = self.dm.settings.get('download_path') or ""
        self.download_frame = DownloadFrame(self, download_path=download_path)
        self.download_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Set callbacks for items in the download list
        self.download_frame.cancel_callback = self.on_cancel_download
        self.download_frame.retry_callback = self.on_retry_download
        
        # Status Bar - Row 3
        self.status_bar = ctk.CTkLabel(self, text="Ready", anchor="w", font=("Arial", 10))
        self.status_bar.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 5))
        
        # === RIGHT COLUMN (Preview) ===
        self.preview_frame = ctk.CTkFrame(self, fg_color="gray20", corner_radius=10)
        self.preview_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=(0, 10), pady=10)
        
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_frame.grid_rowconfigure(1, weight=1)
        
        lbl_preview_title = ctk.CTkLabel(self.preview_frame, text="Preview", font=("Segoe UI", 14, "bold"))
        lbl_preview_title.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Thumbnail Placeholder
        self.lbl_thumbnail = ctk.CTkLabel(
            self.preview_frame, text="🎬\nPaste a URL\nto see preview", 
            width=250, height=160, corner_radius=8, fg_color="gray30",
            font=("Segoe UI", 12)
        )
        self.lbl_thumbnail.grid(row=1, column=0, padx=10, pady=5, sticky="n")
        
        # Video Title Label
        self.lbl_video_title = ctk.CTkLabel(
            self.preview_frame, text="", 
            font=("Segoe UI", 12, "bold"), anchor="w", wraplength=230
        )
        self.lbl_video_title.grid(row=2, column=0, padx=10, pady=(10, 2), sticky="ew")
        
        # Video Info Label (Uploader, Duration)
        self.lbl_video_info = ctk.CTkLabel(
            self.preview_frame, text="", 
            font=("Segoe UI", 10), text_color="gray60", anchor="w"
        )
        self.lbl_video_info.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Loading Indicator Label
        self.lbl_preview_loading = ctk.CTkLabel(
            self.preview_frame, text="", font=("Segoe UI", 10), text_color="orange"
        )
        self.lbl_preview_loading.grid(row=4, column=0, padx=10, pady=5)
        
        # 4. Start Event Queue Check Loop
        self.after(100, self.check_queue)

    def _set_icon(self):
        """
        Sets the application icon for the title bar and taskbar.
        Handles checking logic for both development and frozen (PyInstaller) environments.
        """
        import sys
        from pathlib import Path
        
        try:
            # PyInstaller --onefile extracts files to sys._MEIPASS
            if getattr(sys, 'frozen', False):
                base = Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent))
            else:
                base = Path(__file__).parent.parent.parent
            
            icon_path = base / "src" / "assets" / "icon.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
                # Force Windows taskbar to show the custom icon instead of the default Python icon
                if sys.platform == 'win32':
                    import ctypes
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ytdlp.gui.app")
                logger.info(f"Icon loaded from {icon_path}")
            else:
                logger.warning(f"Icon not found at {icon_path}")
        except Exception as e:
            logger.warning(f"Failed to set icon: {e}")

    # === URL DETECTION ===
    
    def _on_url_change(self, event=None):
        """
        Callback for key release on URL entry.
        Uses a timer to 'debounce' input (wait for user to stop typing).
        """
        if self._url_check_id:
            self.after_cancel(self._url_check_id)
        # Wait 500ms after last keypress before checking URL
        self._url_check_id = self.after(500, self._check_url)

    def _on_url_paste(self, event=None):
        """
        Callback for Ctrl+V paste.
        Checks URL almost immediately.
        """
        self.after(50, self._check_url)

    def _check_url(self):
        """
        Determine if the text in the entry field is a new YouTube URL.
        If valid and new, triggers metadata fetching for preview.
        """
        url = self.entry_url.get().strip()
        if url and url != self.current_url and ("youtube.com" in url or "youtu.be" in url):
            self.current_url = url
            self._fetch_preview(url)

    def _fetch_preview(self, url: str):
        """
        Initiates the metadata fetch process in a background thread.
        Updates UI to show loading state.
        
        Args:
            url: The URL to fetch metadata for.
        """
        self.lbl_preview_loading.configure(text="Loading...")
        self.lbl_video_title.configure(text="")
        self.lbl_video_info.configure(text="")
        self.lbl_thumbnail.configure(image=None, text="")
        self.status_bar.configure(text=f"Fetching preview: {url[:40]}...")
        
        threading.Thread(
            target=self._fetch_metadata_worker,
            args=(url,),
            daemon=True
        ).start()

    def _extract_video_id(self, url: str) -> str:
        """Video ID extraction helper using regex."""
        import re
        patterns = [
            r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'(?:embed/)([a-zA-Z0-9_-]{11})',
            r'(?:shorts/)([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return ""

    def _fetch_metadata_worker(self, url: str):
        """
        Worker thread function to fetch video metadata.
        Tries fast oEmbed first for YouTube, falls back to yt-dlp if needed.
        """
        import time
        import json
        import urllib.request
        import ssl
        
        is_youtube = 'youtube.com' in url or 'youtu.be' in url
        
        if is_youtube:
            # Fast path: YouTube oEmbed API (Much faster than spinning up yt-dlp process)
            try:
                t0 = time.time()
                video_id = self._extract_video_id(url)
                
                oembed_url = f"https://www.youtube.com/oembed?url={urllib.request.quote(url, safe='')}&format=json"
                ctx = ssl.create_default_context()
                req = urllib.request.Request(oembed_url, headers={"User-Agent": "Mozilla/5.0"})
                
                with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
                    data = json.loads(response.read().decode())
                
                t1 = time.time()
                logger.info(f"⏱ oEmbed fetch: {t1-t0:.2f}s")
                
                # Normalize metadata to our internal format
                metadata = {
                    'title': data.get('title', 'Unknown'),
                    'uploader': data.get('author_name', ''),
                    'id': video_id,
                    'webpage_url': url,
                    'thumbnail': f"https://i.ytimg.com/vi/{video_id}/mqdefault.jpg" if video_id else '',
                }
                
                # Schedule UI update on main thread
                self.after(0, lambda m=metadata: self._update_preview(m))
                return
            except Exception as e:
                logger.warning(f"oEmbed failed, falling back to yt-dlp: {e}")
                # Fall through to yt-dlp logic
        
        # Slow path: use yt-dlp --dump-json
        try:
            t0 = time.time()
            ytdlp_path = self.dm.settings.get('ytdlp_path') or ''
            ffmpeg_path = self.dm.settings.get('ffmpeg_path') or ''
            wrapper = YtDlpWrapper(ytdlp_path=ytdlp_path, ffmpeg_path=ffmpeg_path)
            
            cookies_path = self.dm.settings.get('cookies_path') or ''
            cookies_browser = self.dm.settings.get('cookies_browser') or ''
            
            metadata = wrapper.get_metadata(url, cookies_path=cookies_path, cookies_browser=cookies_browser)
            t1 = time.time()
            logger.info(f"⏱ yt-dlp metadata fetch: {t1-t0:.2f}s")
            
            self.after(0, lambda m=metadata: self._update_preview(m))
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Metadata fetch failed: {error_msg}")
            self.after(0, lambda err=error_msg: self._preview_error(err))

    def _update_preview(self, metadata: dict):
        """
        Updates the preview panel with fetched metadata.
        Called on the main thread.
        """
        # Store metadata for use when user clicks "Download"
        self.current_metadata = metadata
        
        title = metadata.get('title', 'Unknown')
        uploader = metadata.get('uploader', '')
        duration = metadata.get('duration_string', '')
        
        self.lbl_video_title.configure(text=title)
        
        info_parts = []
        if uploader:
            info_parts.append(f"👤 {uploader}")
        if duration:
            info_parts.append(f"⏱ {duration}")
        self.lbl_video_info.configure(text=" • ".join(info_parts))
        
        self.lbl_preview_loading.configure(text="")
        self.status_bar.configure(text="Preview loaded. Ready to download.")
        
        # Initiate background thumbnail download
        thumb_url = metadata.get('thumbnail', '')
        
        if thumb_url:
            self.lbl_thumbnail.configure(text="⏳ Loading...")
            threading.Thread(
                target=self._load_thumbnail,
                args=(thumb_url,),
                daemon=True
            ).start()

    def _load_thumbnail(self, url: str):
        """
        Downloads and resizes the thumbnail image in a background thread.
        """
        try:
            from PIL import Image
            import io
            import urllib.request
            import ssl
            import time
            
            t0 = time.time()
            
            # Create SSL context to avoid certification errors
            ctx = ssl.create_default_context()
            
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8, context=ctx) as response:
                data = response.read()
            
            t1 = time.time()
            
            pil_image = Image.open(io.BytesIO(data))
            pil_image = pil_image.resize((250, 160), Image.LANCZOS)
            
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(250, 160))
            
            # Keep reference to image object to prevent garbage collection!
            self._current_thumb = ctk_image
            
            t2 = time.time()
            logger.info(f"⏱ PROFILING THUMB: download={t1-t0:.2f}s, resize={t2-t1:.2f}s")
            
            # Update UI
            self.after(0, lambda: self.lbl_thumbnail.configure(image=self._current_thumb, text=""))
        except Exception as e:
            logger.error(f"Thumbnail load failed: {e}")
            self.after(0, lambda: self.lbl_thumbnail.configure(text="📷 Thumbnail unavailable"))

    def _preview_error(self, error: str):
        """Displays error in preview panel."""
        self.lbl_preview_loading.configure(text="")
        self.lbl_video_title.configure(text=f"Error: {error[:40]}...")
        self.status_bar.configure(text="Failed to load preview")

    # === SETTINGS & OPTIONS ===
    
    def open_settings(self):
        """Opens the Settings Dialog window."""
        SettingsDialog(self)

    def on_mode_change(self, value):
        """
        Enable/Disable quality dropdown based on selected mode.
        """
        if value == "Audio Only":
            self.combo_quality.configure(state="disabled")
            self.combo_quality.set("—")
        else:
            self.combo_quality.configure(state="readonly")
            self.combo_quality.set("Best Quality")

    def _get_quality_format(self) -> str:
        """
        Maps the readable quality selection to a yt-dlp format string.
        """
        quality_map = {
            "Best Quality": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
            "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
        }
        return quality_map.get(self.combo_quality.get(), "bestvideo+bestaudio/best")

    def get_download_options(self) -> dict:
        """
        Collects all user-selected options into a dictionary for the DownloadManager.
        """
        mode = self.download_mode.get()
        return {
            "download_video": self.chk_download_video.get() == 1,
            "audio_only": mode == "Audio Only",
            "save_thumbnail": self.chk_save_thumb.get() == 1,
            "embed_thumbnail": self.chk_embed_thumb.get() == 1,
            "format": self._get_quality_format() if mode != "Audio Only" else None,
        }

    # === DOWNLOAD ACTIONS ===
    
    def _is_valid_url(self, url: str) -> bool:
        """Checks if the URL matches known supported patterns."""
        patterns = [
            r'(https?://)?(www\.)?youtube\.com/watch\?v=',
            r'(https?://)?(www\.)?youtu\.be/',
            r'(https?://)?(www\.)?youtube\.com/shorts/',
            r'(https?://)?(www\.)?twitch\.tv/',
            r'(https?://)?(www\.)?twitter\.com/',
            r'(https?://)?(www\.)?x\.com/',
            r'(https?://)?(www\.)?vimeo\.com/',
            r'(https?://)?(www\.)?dailymotion\.com/',
        ]
        return any(re.search(p, url) for p in patterns)
    
    def on_download_click(self):
        """
        Handles the Download button click.
        Validates URL/Options, starts the download task, and adds it to the list.
        """
        url = self.entry_url.get().strip()
        if not url:
            return
        
        # Validate URL
        if not self._is_valid_url(url):
            self.status_bar.configure(text="⚠️ Invalid or unsupported URL")
            return
        
        options = self.get_download_options()
        
        # Check at least one option is selected
        if not options["download_video"] and not options["save_thumbnail"]:
            self.status_bar.configure(text="Select at least one option to download!")
            return
        
        # Use video title from metadata if available, else fallback to URL
        display_name = self.current_metadata.get('title', url[:50])
        
        self.status_bar.configure(text=f"Starting download: {display_name[:40]}...")
        try:
            task_id = self.dm.start_download(url, options)
            self.download_frame.add_item(task_id, display_name)
            self.entry_url.delete(0, "end")
            self.current_url = ""
            self.current_metadata = {}
        except Exception as e:
            logger.error(f"Failed to start download: {e}")
            self.status_bar.configure(text=f"Error: {e}")

    def on_cancel_download(self, task_id: str):
        """Callback to cancel a specific download task."""
        self.dm.cancel_download(task_id)
        self.status_bar.configure(text=f"Cancelled: {task_id[:8]}...")

    def on_retry_download(self, task_id: str, url: str):
        """Callback to retry a failed download."""
        self.status_bar.configure(text=f"Retrying: {url[:30]}...")
        try:
            options = self.get_download_options()
            new_task_id = self.dm.start_download(url, options)
            # Update the item in the list with the new task ID
            if task_id in self.download_frame.items:
                item = self.download_frame.items.pop(task_id)
                item.task_id = new_task_id
                self.download_frame.items[new_task_id] = item
        except Exception as e:
            logger.error(f"Retry failed: {e}")
            self.status_bar.configure(text=f"Retry error: {e}")

    # === EVENT QUEUE PROCESSING ===
    
    def check_queue(self):
        """
        Periodically checks the thread-safe event queue for messages
        from background threads (progress updates, status changes).
        """
        try:
            while not event_queue.empty():
                msg = event_queue.get_nowait()
                self.handle_message(msg)
        finally:
            # Re-schedule check in 100ms
            self.after(100, self.check_queue)

    def handle_message(self, msg: dict):
        """Dispatches queue messages to the appropriate UI handlers."""
        m_type = msg.get('type')
        payload = msg.get('payload')
        task_id = msg.get('task_id')
        
        if m_type == 'progress':
            self.download_frame.update_item_progress(task_id, payload)
        elif m_type == 'status':
            self.download_frame.update_item_status(task_id, payload)
            self.status_bar.configure(text=str(payload))
        elif m_type == 'error':
            self.download_frame.update_item_status(task_id, f"Error: {payload}")
            logger.error(f"Task {task_id} error: {payload}")
