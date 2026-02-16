import threading
import uuid
import logging
from typing import Dict
from src.services.ytdlp_wrapper import YtDlpWrapper
from src.core.settings_manager import SettingsManager

logger = logging.getLogger(__name__)

class DownloadManager:
    """
    Core Controller for managing download tasks.
    
    Responsibilities:
    - distinct thread spawning for each download.
    - tracking active downloads via unique task IDs.
    - bridging the UI and the yt-dlp wrapper.
    - managing cancellation requests.
    """
    def __init__(self):
        self.active_downloads: Dict[str, YtDlpWrapper] = {}
        self.settings = SettingsManager()

    def start_download(self, url: str, options: dict = None) -> str:
        """
        Initiates a new download task in a separate thread.
        
        Args:
           url (str): The video URL to download.
           options (dict): User-selected options from the UI (audio, quality, thumbnail etc).
           
        Returns:
           str: A unique task ID (UUID) for tracking this download.
        """
        if options is None:
            options = {}
        
        task_id = str(uuid.uuid4())
        
        # Load necessary paths from settings
        ytdlp_path = self.settings.get('ytdlp_path') or ""
        ffmpeg_path = self.settings.get('ffmpeg_path') or ""
        
        # Create a new wrapper instance for this specific task
        wrapper = YtDlpWrapper(ytdlp_path=ytdlp_path, ffmpeg_path=ffmpeg_path)
        
        # Store reference to handle cancellation
        self.active_downloads[task_id] = wrapper
        
        # Configure output path and filename pattern
        naming_pattern = self.settings.get('naming_pattern') or "%(title)s.%(ext)s"
        download_folder = self.settings.get('download_path') or "."
        
        # Ensure extension is handled correctly in the template
        if '%(ext)s' not in naming_pattern:
             output_template = f"{download_folder}/{naming_pattern}.%(ext)s"
        else:
             output_template = f"{download_folder}/{naming_pattern}"
             
        # Get authentication settings
        cookies_path = self.settings.get('cookies_path') or ""
        cookies_browser = self.settings.get('cookies_browser') or ""
        
        # Spawn the worker thread
        thread = threading.Thread(
            target=self._download_worker,
            args=(wrapper, url, task_id, output_template, cookies_path, cookies_browser, options),
            daemon=True
        )
        thread.start()
        
        logger.info(f"Started download task {task_id} for {url} with options {options}")
        return task_id

    def _download_worker(self, wrapper: YtDlpWrapper, url: str, task_id: str, 
                         output_template: str, cookies_path: str, cookies_browser: str, options: dict):
        """
        The background worker function (runs in a separate thread).
        Executes the blocking download call and cleans up upon completion.
        """
        try:
            wrapper.download(
                url, 
                task_id, 
                output_template=output_template, 
                cookies_path=cookies_path, 
                cookies_browser=cookies_browser, 
                options=options
            )
        except Exception as e:
            logger.error(f"Worker thread crashed for {task_id}: {e}")
        finally:
            # Cleanup: remove from active list to release resources
            if task_id in self.active_downloads:
                del self.active_downloads[task_id]

    def cancel_download(self, task_id: str):
        """
        Signals a specific download task to stop.
        """
        if task_id in self.active_downloads:
            logger.info(f"Cancelling task {task_id}")
            # The wrapper's stop() method (renamed from cancel in wrapper update) triggers the threading event
            self.active_downloads[task_id].stop()
