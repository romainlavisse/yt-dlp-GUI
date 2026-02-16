import sys
import os
from pathlib import Path

"""
Main entry point for the yt-dlp GUI application.
Sets up the environment, logging, and launches the main application window.
"""

# Ensure src is in python path to allow imports from src module
sys.path.append(str(Path(__file__).parent / "src"))

if __name__ == "__main__":
    try:
        import logging
        
        # When running as frozen exe (--noconsole), redirect logs to file
        # because stdout/stderr don't exist in no-console mode
        if getattr(sys, 'frozen', False):
            log_dir = Path(sys.executable).parent
            log_file = log_dir / "yt-dlp-gui.log"
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s %(levelname)s: %(message)s',
                filename=str(log_file),
                filemode='w'
            )
        else:
            # Standard console logging for development
            logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
        
        from src.ui.app import App
        
        # Initialize and run the main application
        app = App()
        app.mainloop()
        
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        
        # Try to log the error to a crash file if possible
        try:
            if getattr(sys, 'frozen', False):
                crash_file = Path(sys.executable).parent / "crash.log"
                with open(crash_file, 'w') as f:
                    f.write(error_msg)
            else:
                print(f"Critical Error: {e}")
                traceback.print_exc()
        except:
            pass
        
        # Show error dialog to the user if tkinter is available
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw() # Hide the main window
            messagebox.showerror("yt-dlp GUI - Error", f"Failed to start:\n\n{e}\n\nCheck crash.log for details.")
            root.destroy()
        except:
            pass
