from src.gui.app import WebScraperApp
import tkinter as tk
import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING").upper()
logging.getLogger().setLevel(LOG_LEVEL)

if __name__ == "__main__":
    root = tk.Tk(className=f"regurl")
    app = WebScraperApp(root)
    root.mainloop()