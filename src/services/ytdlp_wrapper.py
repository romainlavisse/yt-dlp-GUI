import subprocess
import threading
import re
import logging
import sys
import shutil
import os
from pathlib import Path
from typing import Optional, Callable
from src.core.queue_manager import put_message

logger = logging.getLogger(__name__)

def _get_bin_dir() -> Path:
    """
    Returns the 'bin' directory path where executables might be stored.
    Handles both frozen (PyInstaller) and source distributions.
    """
    if getattr(sys, 'frozen', False):
        # In frozen mode, the executable is in the parent of the sys.executable
        base_dir = Path(sys.executable).parent
    else:
        # In source mode, go up 3 levels from this file (src/services/ytdlp_wrapper.py -> project_root)
        base_dir = Path(__file__).parent.parent.parent
    return base_dir / "bin"

def _find_ytdlp_executable(custom_path: str = "") -> str:
    """
    Finds the yt-dlp executable path.
    Search Priority: 
    1. Custom path provided in settings
    2. 'bin/' folder in the project directory
    3. virtualenv 'Scripts' or 'bin' folder
    4. System PATH
    
    Raises:
        FileNotFoundError: If yt-dlp executable cannot be found.
    """
    # 1. Check custom path first
    if custom_path:
        custom = Path(custom_path)
        if custom.exists():
            return str(custom)
    
    # 2. Check bin/ folder (useful for portable distribution)
    bin_dir = _get_bin_dir()
    if sys.platform == 'win32':
        bin_ytdlp = bin_dir / 'yt-dlp.exe'
    else:
        bin_ytdlp = bin_dir / 'yt-dlp'
    
    if bin_ytdlp.exists():
        return str(bin_ytdlp)
    
    # 3. Check current virtual environment
    if hasattr(sys, 'prefix') and sys.prefix != sys.base_prefix:
        if sys.platform == 'win32':
            venv_ytdlp = Path(sys.prefix) / 'Scripts' / 'yt-dlp.exe'
        else:
            venv_ytdlp = Path(sys.prefix) / 'bin' / 'yt-dlp'
        
        if venv_ytdlp.exists():
            return str(venv_ytdlp)
    
    # 4. Fallback to system PATH
    found = shutil.which('yt-dlp')
    if found:
        return found
    
    raise FileNotFoundError("yt-dlp not found. Please download it and configure the path in Settings.")

def _get_subprocess_env(ffmpeg_path: str = "") -> dict:
    """
    Prepares the environment variables for the subprocess.
    Ensures that the directory containing ffmpeg and the 'bin' directory are in the system PATH.
    """
    env = os.environ.copy()
    
    extra_paths = []
    
    # Add custom ffmpeg path directory to allow yt-dlp to find it
    if ffmpeg_path:
        ffmpeg_dir = str(Path(ffmpeg_path).parent)
        extra_paths.append(ffmpeg_dir)
    
    # Add project 'bin/' folder to PATH
    bin_dir = _get_bin_dir()
    if bin_dir.exists():
        extra_paths.append(str(bin_dir))
    
    # Prepend new paths to the existing PATH
    existing_path = env.get('PATH', '')
    new_paths = [p for p in extra_paths if p not in existing_path]
    
    if new_paths:
        env['PATH'] = os.pathsep.join(new_paths) + os.pathsep + existing_path
    
    return env


class YtDlpWrapper:
    """
    A wrapper class to manage the execution of yt-dlp subprocesses.
    Handles command construction, execution, output parsing, and cancellation.
    """
    def __init__(self, ytdlp_path: str = "", ffmpeg_path: str = ""):
        self.process: Optional[subprocess.Popen] = None
        self._stop_event = threading.Event()
        self._ytdlp_path = _find_ytdlp_executable(ytdlp_path)
        self._ffmpeg_path = ffmpeg_path
        logger.info(f"Using yt-dlp at: {self._ytdlp_path}")

    def get_metadata(self, url: str, cookies_path: str = "", cookies_browser: str = "") -> dict:
        """
        Fetches video metadata via `yt-dlp --dump-json`.
        This is a blocking call and should typically be run in a background thread.
        
        Args:
            url: Video URL.
            cookies_path: Path to netscape cookies file.
            cookies_browser: Browser name to extract cookies from.
            
        Returns:
            dict: Parsed JSON metadata from yt-dlp.
        """
        cmd = [
            self._ytdlp_path,
            "--dump-json",          # Return JSON data
            "--no-playlist",        # Only get single video metadata
            "--skip-download",      # Do not download content
        ]
        
        # Add cookies configuration if present
        if cookies_path:
            cmd.extend(["--cookies", cookies_path])
        elif cookies_browser:
            cmd.extend(["--cookies-from-browser", cookies_browser])
        
        cmd.append(url)
        
        try:
            env = _get_subprocess_env(self._ffmpeg_path)
            
            # Suppress console window popping up on Windows
            creationflags = 0
            if sys.platform == 'win32':
                creationflags = subprocess.CREATE_NO_WINDOW
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding="utf-8",
                errors="replace",
                env=env,
                creationflags=creationflags
            )
            if result.returncode != 0:
                raise Exception(f"yt-dlp error: {result.stderr}")
            
            # Parse the JSON output
            import json
            return json.loads(result.stdout)
            
        except FileNotFoundError:
            raise Exception("yt-dlp executable not found on PATH")
        except Exception as e:
            logger.error(f"Metadata fetch failed: {e}")
            raise

    def download(self, url: str, task_id: str, output_template: str = "%(title)s.%(ext)s", 
                 cookies_path: str = "", cookies_browser: str = "", options: dict = None):
        """
        Executes the main download process.
        Runs yt-dlp in a subprocess and streams standard output to parse progress.
        
        Args:
            url: The video URL to download.
            task_id: Unique identifier for this download task.
            output_template: Filename template (passed to -o).
            cookies_path: Path to cookies file.
            cookies_browser: Browser to extract cookies from.
            options: Dictionary containing various download flags (audio_only, thumbnail, etc).
            
        Note:
            This method is blocking and monitors the subprocess until completion.
            It must be run in a separate thread.
        """
        if options is None:
            options = {}
        
        # Build the command arguments
        cmd = [
            self._ytdlp_path,
            "--newline",     # Output progress on new lines for easier parsing
            "--no-colors",   # Disable ANSI colors to simplify parsing
            "--no-playlist", # Download only the targeted video
            "-o", output_template,
            # Custom progress template to strictly format the output line for parsing
            "--progress-template", "%(progress._percent_str)s:%(progress._eta_str)s:%(progress._speed_str)s",
        ]
        
        # Skip video download if only thumbnail is requested
        if not options.get("download_video", True):
            cmd.append("--skip-download")
        
        # Process Audio-Only Mode
        if options.get("audio_only") and options.get("download_video", True):
            # Extract audio, convert to mp3, use best quality (0)
            cmd.extend(["-x", "--audio-format", "mp3", "--audio-quality", "0"])
        elif options.get("format"):
            # Select specific video quality format
            cmd.extend(["-f", options["format"]])
        
        # Thumbnail Options
        if options.get("save_thumbnail"):
            cmd.append("--write-thumbnail")
            cmd.extend(["--convert-thumbnails", "jpg"])
        if options.get("embed_thumbnail") and options.get("download_video", True):
            cmd.append("--embed-thumbnail")
            cmd.extend(["--convert-thumbnails", "jpg"])
            # Force MP4 container if video is downloaded, as MKV often has issues with embedded thumbnails in Windows
            if not options.get("audio_only"):
                cmd.extend(["--merge-output-format", "mp4"])
        
        # Set FFmpeg location if provided
        if self._ffmpeg_path:
            from pathlib import Path
            ffmpeg_dir = str(Path(self._ffmpeg_path).parent)
            cmd.extend(["--ffmpeg-location", ffmpeg_dir])
        
        # Add Cookie Authentication
        if cookies_path:
            cmd.extend(["--cookies", cookies_path])
        elif cookies_browser:
            cmd.extend(["--cookies-from-browser", cookies_browser])
        
        cmd.append(url)
        
        logger.info(f"yt-dlp command: {' '.join(cmd)}")

        try:
            # Prepare environment
            env = _get_subprocess_env(self._ffmpeg_path)
            
            # Suppress console window on Windows
            creationflags = 0
            if sys.platform == 'win32':
                creationflags = subprocess.CREATE_NO_WINDOW

            # Start the subprocess with pipes for stdout/stderr
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Merge stderr into stdout
                universal_newlines=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                creationflags=creationflags
            )

            # Continuous loop to read output line by line
            while True:
                # Check for external cancellation request
                if self._stop_event.is_set():
                    self.process.terminate()
                    break

                line = self.process.stdout.readline()
                # If EOF and process finished
                if not line and self.process.poll() is not None:
                    break
                
                if line:
                    stripped = line.strip()
                    logger.info(f"[yt-dlp] {stripped}")
                    self._parse_output(stripped, task_id)
            
            # Wait for process to fully exit and get return code
            rc = self.process.poll()
            
            if rc == 0:
                # Success
                put_message("status", "Download Completed", task_id)
                put_message("progress", {"percent": "100%", "eta": "00:00", "speed": "0MiB/s"}, task_id)
            elif self._stop_event.is_set():
                # Cancelled by user
                 put_message("status", "Download Cancelled", task_id)
            else:
                # Error occurred
                 put_message("error", f"Process failed (exit code {rc})", task_id)

        except Exception as e:
            logger.exception("Wrapper download fatal error")
            put_message("error", str(e), task_id)
        finally:
            self.process = None
            self._stop_event.clear()

    def cancel(self):
        """
        Signals the download loop to stop and terminate the process.
        """
        if self.process:
            self._stop_event.set()
            # Actual termination happens inside the loop to ensure clean exit

    def _parse_output(self, line: str, task_id: str):
        """
        Parses a single line of yt-dlp stdout and pushes progress updates to the event queue.
        
        Args:
            line: The stdout line string.
            task_id: The ID of the task to update.
        """
        
        # Regex to find percentage (e.g., "45.2%")
        percent_match = re.search(r'(\d{1,3}\.\d)%', line)
        if percent_match:
            percent = percent_match.group(1) + "%"
            # Send progress update
            put_message("progress", {"percent": percent, "raw": line}, task_id)
        elif '[download]' in line.lower() or '[merger]' in line.lower():
            # General status update
            put_message("status", line, task_id)
        elif 'Downloading' in line or 'Extracting' in line:
            # Other known status lines
            put_message("status", line, task_id)
        
        # Forward everything to log as well
        put_message("log", line, task_id)

