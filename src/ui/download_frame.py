import customtkinter as ctk
from typing import Dict, Callable
from src.ui.components.download_item import DownloadItem

class DownloadFrame(ctk.CTkScrollableFrame):
    """
    Scrollable Container for DownloadItems.
    
    Responsibilities:
    - Manages the list of active/completed download widgets.
    - Handles adding/removing items dynamically.
    - Routes updates from the DownloadManager to specific DownloadItems.
    """
    def __init__(self, master, download_path: str = "", **kwargs):
        super().__init__(master, **kwargs)
        self.items: Dict[str, DownloadItem] = {}
        self.download_path = download_path
        
        # Callbacks (assigned by the parent App controller)
        self.cancel_callback: Callable[[str], None] = lambda tid: None
        self.retry_callback: Callable[[str, str], None] = lambda tid, url: None
        
        # Configure grid layout so items expand to full width
        self.grid_columnconfigure(0, weight=1)

    def set_download_path(self, path: str):
        """Updates the default download path for new items."""
        self.download_path = path

    def add_item(self, task_id: str, display_name: str) -> DownloadItem:
        """
        Creates and adds a new DownloadItem widget to the list.
        
        Args:
            task_id (str): Unique ID of the download task.
            display_name (str): Title or URL to display initially.
            
        Returns:
            DownloadItem: The created widget instance.
        """
        item = DownloadItem(self, task_id, display_name, download_path=self.download_path)
        
        # Connect item callbacks to frame's callbacks (which bubble up to App)
        item.cancel_callback = self.cancel_callback
        item.retry_callback = self.retry_callback
        
        # Add to the next available row
        row_idx = len(self.items)
        item.grid(row=row_idx, column=0, padx=5, pady=5, sticky="ew")
        
        self.items[task_id] = item
        return item

    def remove_item(self, task_id: str):
        """
        Removes a DownloadItem from the UI by task_id.
        Triggers a layout refresh to close gaps.
        """
        if task_id in self.items:
            item = self.items.pop(task_id)
            item.destroy()
            self._regrid_items()

    def _regrid_items(self):
        """
        Re-packs all items in the grid to remove gaps after deletion.
        """
        for idx, item in enumerate(self.items.values()):
            item.grid(row=idx, column=0, padx=5, pady=5, sticky="ew")

    def update_item_progress(self, task_id: str, payload: dict):
        """Routes progress updates to the correct child widget."""
        if task_id in self.items:
            self.items[task_id].update_progress(payload)

    def update_item_status(self, task_id: str, status: str):
        """Routes status updates to the correct child widget."""
        if task_id in self.items:
            self.items[task_id].update_status(status)
