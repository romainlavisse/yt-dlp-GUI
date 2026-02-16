import customtkinter as ctk
import subprocess
import os
from typing import Callable, Any
from pathlib import Path

class DownloadItem(ctk.CTkFrame):
    """
    Composite widget representing a single download task in the list.
    Displays:
    - Status Icon (Play/Check/Cross)
    - Video Title
    - Progress Bar
    - Status Text (Percentage, Speed, ETA)
    - Action Buttons (Cancel, Retry, Open Folder)
    """
    def __init__(self, master, task_id: str, url: str, download_path: str = "", **kwargs):
        super().__init__(master, **kwargs)
        self.task_id = task_id
        self.url = url
        self.download_path = download_path
        self.is_completed = False
        self.is_error = False
        
        # Grid Layout Configuration
        self.grid_columnconfigure(1, weight=1) # Column 1 (Title/Progress) expands to fill space
        
        # 1. Status Icon / Placeholder
        self.lbl_icon = ctk.CTkLabel(self, text="▶", width=40, corner_radius=5, fg_color="gray30")
        self.lbl_icon.grid(row=0, column=0, rowspan=2, padx=10, pady=5, sticky="ns")
        
        # 2. Title and Status Labels
        self.lbl_title = ctk.CTkLabel(self, text=url, font=("Segoe UI", 12, "bold"), anchor="w")
        self.lbl_title.grid(row=0, column=1, padx=5, pady=(5,0), sticky="ew")
        
        self.lbl_status = ctk.CTkLabel(self, text="Initializing...", font=("Segoe UI", 10), text_color="gray70", anchor="w")
        self.lbl_status.grid(row=0, column=2, padx=10, pady=(5,0), sticky="e")

        # 3. Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self, height=8)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=1, columnspan=2, padx=5, pady=(0,5), sticky="ew")

        # 4. Action Buttons Container
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid(row=0, column=3, rowspan=2, padx=5, pady=5)
        
        # Cancel Button (Visible by default)
        self.btn_cancel = ctk.CTkButton(
            self.actions_frame, text="✕", width=30, height=30, 
            fg_color="transparent", border_width=1, text_color="red",
            command=self.on_cancel
        )
        self.btn_cancel.pack(side="left", padx=2)
        
        # Retry Button (Hidden by default, shown on error)
        self.btn_retry = ctk.CTkButton(
            self.actions_frame, text="↻", width=30, height=30,
            fg_color="transparent", border_width=1, text_color="orange",
            command=self.on_retry
        )
        
        # Open Folder Button (Hidden by default, shown on completion)
        self.btn_open_folder = ctk.CTkButton(
            self.actions_frame, text="📁", width=30, height=30,
            fg_color="transparent", border_width=1, text_color="green",
            command=self.on_open_folder
        )
        
        # Callbacks (to be assigned by the parent controller)
        self.cancel_callback: Callable[[str], None] = lambda tid: None
        self.retry_callback: Callable[[str, str], None] = lambda tid, url: None

    def update_progress(self, payload: dict):
        """
        Updates the UI elements with progress data from the background thread.
        Payload expected: {'percent': '45.5%', 'speed': '2MB/s', 'eta': '00:30'}
        """
        if 'percent' in payload:
            try:
                # Convert "45.5%" string to 0.455 float for progress bar
                p_str = payload['percent'].replace('%','')
                val = float(p_str) / 100.0
                self.progress_bar.set(val)
            except:
                pass
        
        # Update status text
        status_text = f"{payload.get('percent', '?')} • {payload.get('speed', '')} • ETA {payload.get('eta', '')}"
        self.lbl_status.configure(text=status_text)

    def update_status(self, status: str):
        """
        Updates the item state based on status messages (Complete, Error, etc).
        """
        self.lbl_status.configure(text=status)
        
        if "Complete" in status:
            self.is_completed = True
            self.progress_bar.set(1)
            self.progress_bar.configure(progress_color="green")
            self.lbl_icon.configure(text="✓", fg_color="green")
            
            # Swap buttons: Cancel -> Open Folder
            self.btn_cancel.pack_forget()
            self.btn_open_folder.pack(side="left", padx=2)
            
        elif "Error" in status or "failed" in status.lower():
            self.is_error = True
            self.progress_bar.configure(progress_color="red")
            self.lbl_icon.configure(text="✗", fg_color="red")
            
            # Swap buttons: Cancel -> Retry
            self.btn_cancel.pack_forget()
            self.btn_retry.pack(side="left", padx=2)

    def on_cancel(self):
        """Trigger cancellation via callback."""
        if self.cancel_callback:
            self.cancel_callback(self.task_id)
        self.btn_cancel.configure(state="disabled")
        self.lbl_status.configure(text="Cancelling...")

    def on_retry(self):
        """
        Trigger retry via callback.
        Resets the UI state for a fresh attempt.
        """
        if self.retry_callback:
            self.retry_callback(self.task_id, self.url)
        
        # Reset UI to initial state
        self.is_error = False
        self.progress_bar.set(0)
        self.progress_bar.configure(progress_color=["#3B8ED0", "#1F6AA5"]) # Default blue theme colors
        self.lbl_icon.configure(text="▶", fg_color="gray30")
        self.lbl_status.configure(text="Retrying...")
        
        # Hide Retry, Show Cancel
        self.btn_retry.pack_forget()
        self.btn_cancel.pack(side="left", padx=2)
        self.btn_cancel.configure(state="normal")

    def on_open_folder(self):
        """
        Opens the configured download folder in the OS file explorer.
        Supports Windows (startfile) and Linux/xdg-open.
        """
        if self.download_path and os.path.isdir(self.download_path):
            try:
                if os.name == 'nt':
                    os.startfile(self.download_path)
                else:
                    subprocess.run(["xdg-open", self.download_path])
            except Exception as e:
                print(f"Error opening folder: {e}")

    def set_title(self, title: str):
        self.lbl_title.configure(text=title)
    
    def set_download_path(self, path: str):
        self.download_path = path
