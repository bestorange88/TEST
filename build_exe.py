"""Build script to create a standalone EXE using PyInstaller.

Usage:
    pip install pyinstaller
    python build_exe.py
"""

import subprocess
import sys


def build():
    """Build the application as a standalone EXE."""
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=EnglishLyricsReader",
        "--onefile",
        "--windowed",
        "--add-data=english_lyrics_reader;english_lyrics_reader",
        "--hidden-import=edge_tts",
        "--hidden-import=pygame",
        "--hidden-import=asyncio",
        "--hidden-import=aiohttp",
        "--collect-all=edge_tts",
        "run.py",
    ]

    print("Building EXE with PyInstaller...")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, check=False)
    if result.returncode == 0:
        print("\nBuild successful! EXE is in the 'dist' folder.")
    else:
        print(f"\nBuild failed with return code {result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    build()
