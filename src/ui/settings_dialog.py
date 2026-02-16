import customtkinter as ctk
from tkinter import filedialog
import webbrowser
from src.core.settings_manager import SettingsManager

class SettingsDialog(ctk.CTkToplevel):
    """
    Modal dialog for application settings.
    Allows users to configure download paths, authentication (cookies), and external dependencies (yt-dlp/ffmpeg).
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Settings")
        self.geometry("550x600")
        self.resizable(False, False)
        
        self.settings = SettingsManager()
        
        # Make the window modal (blocks interaction with main window)
        self.transient(master)
        self.grab_set()
        
        # Setup Grid Layout
        self.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # === DOWNLOAD PATH SECTION ===
        lbl_section1 = ctk.CTkLabel(self, text="📁 Downloads", font=("Segoe UI", 14, "bold"))
        lbl_section1.grid(row=row, column=0, columnspan=3, padx=15, pady=(15, 5), sticky="w")
        row += 1
        
        # Download Folder
        lbl_dl_path = ctk.CTkLabel(self, text="Folder:")
        lbl_dl_path.grid(row=row, column=0, padx=15, pady=5, sticky="e")
        
        self.entry_dl_path = ctk.CTkEntry(self, width=280)
        self.entry_dl_path.insert(0, self.settings.get('download_path') or "")
        self.entry_dl_path.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        
        btn_browse_dl = ctk.CTkButton(self, text="...", width=30, command=self.browse_folder)
        btn_browse_dl.grid(row=row, column=2, padx=(0, 15), pady=5)
        row += 1
        
        # Naming Pattern Configuration
        lbl_pattern = ctk.CTkLabel(self, text="Pattern:")
        lbl_pattern.grid(row=row, column=0, padx=15, pady=5, sticky="e")
        
        default_pattern = "%(upload_date>%Y.%m.%d)s.%(title)s [%(id)s].%(ext)s"
        self.entry_pattern = ctk.CTkEntry(self, width=280, placeholder_text=default_pattern)
        self.entry_pattern.insert(0, self.settings.get('naming_pattern') or default_pattern)
        self.entry_pattern.grid(row=row, column=1, columnspan=2, padx=(5, 15), pady=5, sticky="ew")
        row += 1
        
        # Hint for naming variables
        lbl_hint = ctk.CTkLabel(
            self, text="Variables: %(title)s, %(uploader)s, %(upload_date>%Y.%m.%d)s, %(id)s",
            font=("Segoe UI", 9), text_color="gray60"
        )
        lbl_hint.grid(row=row, column=1, columnspan=2, padx=5, pady=0, sticky="w")
        row += 1
        
        # === AUTHENTICATION SECTION ===
        lbl_section2 = ctk.CTkLabel(self, text="🍪 Authentication (YouTube)", font=("Segoe UI", 14, "bold"))
        lbl_section2.grid(row=row, column=0, columnspan=3, padx=15, pady=(15, 5), sticky="w")
        row += 1
        
        # Cookies File Path
        lbl_file = ctk.CTkLabel(self, text="cookies.txt File:")
        lbl_file.grid(row=row, column=0, padx=15, pady=5, sticky="e")
        
        self.entry_cookies_path = ctk.CTkEntry(self, width=280, placeholder_text="Optional...")
        self.entry_cookies_path.insert(0, self.settings.get('cookies_path') or "")
        self.entry_cookies_path.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        
        btn_browse_cookies = ctk.CTkButton(self, text="...", width=30, command=self.browse_cookies)
        btn_browse_cookies.grid(row=row, column=2, padx=(0, 15), pady=5)
        row += 1
        
        # === DEPENDENCIES SECTION ===
        lbl_section3 = ctk.CTkLabel(self, text="⚙️ Dependencies", font=("Segoe UI", 14, "bold"))
        lbl_section3.grid(row=row, column=0, columnspan=3, padx=15, pady=(15, 5), sticky="w")
        row += 1
        
        # yt-dlp Executable Path
        lbl_ytdlp = ctk.CTkLabel(self, text="yt-dlp.exe:")
        lbl_ytdlp.grid(row=row, column=0, padx=15, pady=5, sticky="e")
        
        self.entry_ytdlp_path = ctk.CTkEntry(self, width=240, placeholder_text="Auto (PATH)")
        ytdlp_path = self.settings.get('ytdlp_path') or ""
        if ytdlp_path:
            self.entry_ytdlp_path.insert(0, ytdlp_path)
        self.entry_ytdlp_path.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        
        # Container for yt-dlp buttons (Browse + Download)
        btn_frame_ytdlp = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame_ytdlp.grid(row=row, column=2, padx=(0, 15), pady=5)
        
        btn_browse_ytdlp = ctk.CTkButton(btn_frame_ytdlp, text="...", width=30, command=self.browse_ytdlp)
        btn_browse_ytdlp.pack(side="left", padx=2)
        
        btn_dl_ytdlp = ctk.CTkButton(btn_frame_ytdlp, text="⬇", width=30, fg_color="green",
                                      command=lambda: webbrowser.open("https://github.com/yt-dlp/yt-dlp/releases/latest"))
        btn_dl_ytdlp.pack(side="left", padx=2)
        row += 1
        
        # FFmpeg Executable Path
        lbl_ffmpeg = ctk.CTkLabel(self, text="ffmpeg.exe:")
        lbl_ffmpeg.grid(row=row, column=0, padx=15, pady=5, sticky="e")
        
        self.entry_ffmpeg_path = ctk.CTkEntry(self, width=240, placeholder_text="Auto (PATH)")
        ffmpeg_path = self.settings.get('ffmpeg_path') or ""
        if ffmpeg_path:
            self.entry_ffmpeg_path.insert(0, ffmpeg_path)
        self.entry_ffmpeg_path.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        
        # Container for FFmpeg buttons (Browse + Download)
        btn_frame_ffmpeg = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame_ffmpeg.grid(row=row, column=2, padx=(0, 15), pady=5)
        
        btn_browse_ffmpeg = ctk.CTkButton(btn_frame_ffmpeg, text="...", width=30, command=self.browse_ffmpeg)
        btn_browse_ffmpeg.pack(side="left", padx=2)
        
        btn_dl_ffmpeg = ctk.CTkButton(btn_frame_ffmpeg, text="⬇", width=30, fg_color="green",
                                       command=lambda: webbrowser.open("https://github.com/BtbN/FFmpeg-Builds/releases"))
        btn_dl_ffmpeg.pack(side="left", padx=2)
        row += 1

        # Deno Installation Command
        lbl_deno = ctk.CTkLabel(self, text="Deno (Install):")
        lbl_deno.grid(row=row, column=0, padx=15, pady=5, sticky="e")

        # Command Container (Darker background for code look)
        cmd_frame = ctk.CTkFrame(self, fg_color="gray10", corner_radius=6)
        cmd_frame.grid(row=row, column=1, padx=5, pady=5, sticky="ew")

        self.lbl_deno_cmd = ctk.CTkLabel(cmd_frame, text="irm https://deno.land/install.ps1 | iex",
                                         font=("Consolas", 11), text_color="gray80", anchor="w")
        self.lbl_deno_cmd.pack(side="left", padx=10, pady=5, fill="x", expand=True)

        btn_copy_deno = ctk.CTkButton(self, text="Copy", width=60,
                                      command=self.copy_deno_command)
        btn_copy_deno.grid(row=row, column=2, padx=(0, 15), pady=5)
        row += 1
        
        # === ACTION BUTTONS ===
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        btn_save = ctk.CTkButton(btn_frame, text="Save", command=self.save_settings, fg_color="green")
        btn_save.pack(side="left", padx=10)
        
        btn_cancel = ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy, fg_color="gray")
        btn_cancel.pack(side="right", padx=10)

    def browse_folder(self):
        """Open dialog to select download folder."""
        path = filedialog.askdirectory(title="Select Download Folder")
        if path:
            self.entry_dl_path.delete(0, "end")
            self.entry_dl_path.insert(0, path)

    def browse_cookies(self):
        """Open dialog to select cookies file."""
        path = filedialog.askopenfilename(
            title="Select cookies.txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if path:
            self.entry_cookies_path.delete(0, "end")
            self.entry_cookies_path.insert(0, path)

    def browse_ytdlp(self):
        """Open dialog to select yt-dlp executable."""
        path = filedialog.askopenfilename(
            title="Select yt-dlp.exe",
            filetypes=[("Executable", "*.exe"), ("All Files", "*.*")]
        )
        if path:
            self.entry_ytdlp_path.delete(0, "end")
            self.entry_ytdlp_path.insert(0, path)

    def browse_ffmpeg(self):
        """Open dialog to select ffmpeg executable."""
        path = filedialog.askopenfilename(
            title="Select ffmpeg.exe",
            filetypes=[("Executable", "*.exe"), ("All Files", "*.*")]
        )
        if path:
            self.entry_ffmpeg_path.delete(0, "end")
            self.entry_ffmpeg_path.insert(0, path)

    def copy_deno_command(self):
        """Copy Deno install command to clipboard."""
        self.clipboard_clear()
        self.clipboard_append(self.lbl_deno_cmd.cget("text"))
        self.update()

    def save_settings(self):
        """Save settings to config file and close dialog."""
        self.settings.set('download_path', self.entry_dl_path.get())
        self.settings.set('naming_pattern', self.entry_pattern.get())
        self.settings.set('cookies_path', self.entry_cookies_path.get())
        self.settings.set('ytdlp_path', self.entry_ytdlp_path.get())
        self.settings.set('ffmpeg_path', self.entry_ffmpeg_path.get())
        self.destroy()

