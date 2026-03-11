"""Entry point for English Lyrics Reader application."""

import tkinter as tk
from english_lyrics_reader.app import EnglishLyricsReader


def main():
    """Launch the English Lyrics Reader application."""
    root = tk.Tk()

    # Set application icon (if available)
    try:
        root.iconbitmap(default="")
    except tk.TclError:
        pass

    app = EnglishLyricsReader(root)

    # Handle window close
    def on_closing():
        app.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
