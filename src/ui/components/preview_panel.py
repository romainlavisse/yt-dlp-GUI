import customtkinter as ctk
from PIL import Image
import io
import urllib.request
import threading
from typing import Callable, Optional

class PreviewPanel(ctk.CTkFrame):
    """
    Panel showing video metadata preview before download.
    Displays:
    - Video Thumbnail
    - Title
    - Uploader and Duration
    - "Confirm Download" control (checkbox + button)
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="gray20", corner_radius=10)
        
        self.current_metadata: dict = {}
        self.thumbnail_image: Optional[ctk.CTkImage] = None
        
        # Callbacks
        self.on_confirm_download: Callable[[], None] = lambda: None
        
        # Grid Layout Configuration
        self.grid_columnconfigure(1, weight=1)
        
        # 1. Thumbnail Placeholder (Left Side)
        self.lbl_thumbnail = ctk.CTkLabel(
            self, text="🎬", width=120, height=80, 
            corner_radius=8, fg_color="gray30"
        )
        self.lbl_thumbnail.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="ns")
        
        # 2. Main Title Label
        self.lbl_title = ctk.CTkLabel(
            self, text="Paste a URL to preview...", 
            font=("Segoe UI", 14, "bold"), anchor="w", wraplength=400
        )
        self.lbl_title.grid(row=0, column=1, padx=10, pady=(10, 2), sticky="ew")
        
        # 3. Info Label (Uploader / Duration)
        self.lbl_info = ctk.CTkLabel(
            self, text="", font=("Segoe UI", 11), 
            text_color="gray60", anchor="w"
        )
        self.lbl_info.grid(row=1, column=1, padx=10, pady=0, sticky="ew")
        
        # 4. Confirmation Controls
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=2, column=1, padx=10, pady=(5, 10), sticky="ew")
        
        self.chk_confirm = ctk.CTkCheckBox(
            self.controls_frame, text="Download this video", 
            font=("Segoe UI", 11)
        )
        self.chk_confirm.select()  # Checked by default
        self.chk_confirm.pack(side="left", padx=(0, 15))
        
        self.btn_confirm = ctk.CTkButton(
            self.controls_frame, text="✓ Confirm Download", 
            fg_color="green", hover_color="darkgreen",
            command=self._on_confirm_click
        )
        self.btn_confirm.pack(side="left")
        self.btn_confirm.configure(state="disabled")  # Disabled until metadata loaded
        
        # Loading indicator (text next to buttons)
        self.lbl_loading = ctk.CTkLabel(
            self.controls_frame, text="", font=("Segoe UI", 10), text_color="orange"
        )
        self.lbl_loading.pack(side="left", padx=10)
        
        # Initially hidden until needed
        self.grid_remove()

    def show(self):
        """Shows the preview panel."""
        self.grid()

    def hide(self):
        """Hides the preview panel."""
        self.grid_remove()

    def set_loading(self, loading: bool):
        """
        Updates the UI to reflect loading state.
        Disables confirmation button while loading.
        """
        if loading:
            self.lbl_loading.configure(text="Loading...")
            self.btn_confirm.configure(state="disabled")
        else:
            self.lbl_loading.configure(text="")

    def update_metadata(self, metadata: dict):
        """
        Updates the preview UI with fetched video metadata.
        Downloads the thumbnail in a background thread.
        """
        self.current_metadata = metadata
        
        title = metadata.get('title', 'Unknown Title')
        uploader = metadata.get('uploader', '')
        duration = metadata.get('duration_string', '')
        
        self.lbl_title.configure(text=title)
        
        info_parts = []
        if uploader:
            info_parts.append(f"👤 {uploader}")
        if duration:
            info_parts.append(f"⏱ {duration}")
        self.lbl_info.configure(text=" • ".join(info_parts))
        
        # Enable confirm button now that we have data
        self.btn_confirm.configure(state="normal")
        self.set_loading(False)
        
        # Trigger background thumbnail download
        thumb_url = metadata.get('thumbnail')
        if thumb_url:
            threading.Thread(
                target=self._load_thumbnail,
                args=(thumb_url,),
                daemon=True
            ).start()

    def _load_thumbnail(self, url: str):
        """
        Downloads thumbnail image from URL in a background thread
        and updates the UI safely.
        """
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                data = response.read()
            
            pil_image = Image.open(io.BytesIO(data))
            pil_image = pil_image.resize((120, 80), Image.LANCZOS)
            
            self.thumbnail_image = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size=(120, 80)
            )
            
            # Update UI on main thread
            self.after(0, lambda: self.lbl_thumbnail.configure(
                image=self.thumbnail_image, text=""
            ))
        except Exception as e:
            print(f"Thumbnail load failed: {e}")

    def _on_confirm_click(self):
        """Called when user clicks the Confirm Download button."""
        if self.chk_confirm.get() == 1:
            self.on_confirm_download()
        else:
            # Checkbox not checked - just hide the panel
            self.hide()

    def is_download_confirmed(self) -> bool:
        """Returns True if the download checkbox is currently checked."""
        return self.chk_confirm.get() == 1

    def clear(self):
        """Resets the preview panel to its initial state."""
        self.current_metadata = {}
        self.lbl_title.configure(text="Paste a URL to preview...")
        self.lbl_info.configure(text="")
        self.lbl_thumbnail.configure(image=None, text="🎬")
        self.btn_confirm.configure(state="disabled")
        self.chk_confirm.select()
