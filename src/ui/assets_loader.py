import os
from pathlib import Path
from PIL import Image
import customtkinter as ctk
from typing import Optional

class AssetsLoader:
    """
    Utility class for loading and caching application assets (images, icons).
    Handles path resolution for both development environments and frozen (PyInstaller) builds.
    """
    
    # Define base asset directories
    # Note: This logic might need adjustment if running as frozen exe (sys._MEIPASS),
    # but currently relies on relative paths from this file.
    ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"
    IMAGES_DIR = ASSETS_DIR / "images"

    @staticmethod
    def load_image(filename: str, size: tuple[int, int] = (20, 20)) -> Optional[ctk.CTkImage]:
        """
        Loads an image file and converts it to a CustomTkinter Image object.
        
        Args:
            filename (str): Name of the file (e.g., 'logo.png').
            size (tuple): Target size for the image (width, height).
            
        Returns:
            ctk.CTkImage | None: The loaded image object, or None if not found/error.
        """
        # Try finding in images subdirectory first
        path = AssetsLoader.IMAGES_DIR / filename
        if not path.exists():
            # Fallback to root assets directory
            path = AssetsLoader.ASSETS_DIR / filename
        
        if path.exists():
            try:
                pil_image = Image.open(path)
                return ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=size)
            except Exception as e:
                print(f"Failed to load image {filename}: {e}")
                return None
        return None

    @staticmethod
    def load_icon(filename: str) -> Optional[str]:
        """
        Resolves the absolute path to an icon file.
        Useful for window icons (.ico) which require a file path string.
        """
        path = AssetsLoader.ASSETS_DIR / filename
        return str(path) if path.exists() else None
