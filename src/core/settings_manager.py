import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Default configuration settings
DEFAULT_CONFIG = {
    "download_path": str(Path.home() / "Downloads"),
    "format": "bestvideo+bestaudio/best",
    "theme": "Dark",
    "collision_mode": "overwrite",
    "cookies_path": "",  # Path to cookies.txt file
    "cookies_browser": "",  # Browser name for --cookies-from-browser
    "naming_pattern": "%(upload_date>%Y.%m.%d)s.%(title)s [%(id)s].%(ext)s",  # Output file naming pattern
    "ytdlp_path": "",  # Custom path to yt-dlp.exe (empty = auto)
    "ffmpeg_path": "",  # Custom path to ffmpeg.exe (empty = auto)
}

class SettingsManager:
    """
    Singleton class for managing application configuration.
    Handles loading, saving, and accessing settings from a JSON file.
    
    The singleton pattern ensures all parts of the app share the same configuration state.
    """
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        """Standard Singleton implementation."""
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """
        Loads configuration from 'config.json' in the application root.
        If file doesn't exist or is invalid, falls back to DEFAULT_CONFIG.
        """
        self.config_path = Path("config.json")
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
                
                # Merge with defaults to ensure all keys exist (schema migration)
                for k, v in DEFAULT_CONFIG.items():
                    if k not in self._config:
                        self._config[k] = v
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                self._config = DEFAULT_CONFIG.copy()
        else:
            # First run: create default config file
            self._config = DEFAULT_CONFIG.copy()
            self.save_config()

    def save_config(self):
        """
        Persists the current configuration state to 'config.json'.
        Should be called after any set() operation.
        """
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key: str) -> Any:
        """
        Retrieves a setting value.
        Returns validated default if key is missing (safety fallback).
        """
        return self._config.get(key, DEFAULT_CONFIG.get(key))

    def set(self, key: str, value: Any):
        """
        Updates a setting value and immediately persists to disk.
        """
        self._config[key] = value
        self.save_config()
