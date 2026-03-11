"""Setup script for English Lyrics Reader."""

from setuptools import setup, find_packages

setup(
    name="english-lyrics-reader",
    version="1.0.0",
    description="A desktop GUI application for reading English lyrics with TTS",
    author="English Lyrics Reader",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "edge-tts>=6.1.0",
        "pygame>=2.5.0",
    ],
    entry_points={
        "console_scripts": [
            "lyrics-reader=english_lyrics_reader.__main__:main",
        ],
    },
)
