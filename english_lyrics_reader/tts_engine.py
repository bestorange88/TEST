"""TTS Engine module using edge-tts for text-to-speech functionality."""

import asyncio
import os
from typing import List, Optional, Callable

import edge_tts

from english_lyrics_reader.constants import DEFAULT_VOICE


async def get_available_voices() -> List[dict]:
    """Fetch available voices from edge-tts."""
    voices = await edge_tts.list_voices()
    return voices


def get_voices_sync() -> List[dict]:
    """Synchronous wrapper to get available voices."""
    loop = asyncio.new_event_loop()
    try:
        voices = loop.run_until_complete(get_available_voices())
        return voices
    finally:
        loop.close()


def get_english_voices(voices: List[dict]) -> List[str]:
    """Filter and return English voice short names."""
    english_voices = [
        v["ShortName"] for v in voices if v.get("Locale", "").startswith("en-")
    ]
    return sorted(english_voices)


def get_chinese_voices(voices: List[dict]) -> List[str]:
    """Filter and return Chinese voice short names."""
    chinese_voices = [
        v["ShortName"] for v in voices if v.get("Locale", "").startswith("zh-")
    ]
    return sorted(chinese_voices)


async def synthesize_to_file(
    text: str,
    output_path: str,
    voice: str = DEFAULT_VOICE,
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
) -> str:
    """Synthesize text to an audio file.

    Args:
        text: The text to synthesize.
        output_path: Path to save the audio file.
        voice: Voice name to use.
        rate: Speech rate (e.g., '+0%', '-50%', '+50%').
        volume: Volume level (e.g., '+0%', '-50%', '+50%').
        pitch: Pitch level (e.g., '+0Hz', '-50Hz', '+50Hz').

    Returns:
        The output file path.
    """
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch,
    )
    await communicate.save(output_path)
    return output_path


def synthesize_to_file_sync(
    text: str,
    output_path: str,
    voice: str = DEFAULT_VOICE,
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
) -> str:
    """Synchronous wrapper for synthesize_to_file."""
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(
            synthesize_to_file(text, output_path, voice, rate, volume, pitch)
        )
        return result
    finally:
        loop.close()


async def synthesize_to_bytes(
    text: str,
    voice: str = DEFAULT_VOICE,
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
) -> bytes:
    """Synthesize text and return audio bytes.

    Args:
        text: The text to synthesize.
        voice: Voice name to use.
        rate: Speech rate.
        volume: Volume level.
        pitch: Pitch level.

    Returns:
        Audio data as bytes.
    """
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch,
    )
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data


def synthesize_to_bytes_sync(
    text: str,
    voice: str = DEFAULT_VOICE,
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
) -> bytes:
    """Synchronous wrapper for synthesize_to_bytes."""
    loop = asyncio.new_event_loop()
    try:
        result = loop.run_until_complete(
            synthesize_to_bytes(text, voice, rate, volume, pitch)
        )
        return result
    finally:
        loop.close()


async def synthesize_lines_to_folder(
    lines: List[str],
    output_folder: str,
    voice: str = DEFAULT_VOICE,
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> List[str]:
    """Synthesize multiple lines to individual files in a folder.

    Args:
        lines: List of text lines to synthesize.
        output_folder: Folder to save audio files.
        voice: Voice name to use.
        rate: Speech rate.
        volume: Volume level.
        pitch: Pitch level.
        progress_callback: Optional callback(current, total) for progress updates.

    Returns:
        List of output file paths.
    """
    os.makedirs(output_folder, exist_ok=True)
    output_files = []

    for i, line in enumerate(lines):
        if not line.strip():
            continue
        filename = f"line_{i + 1:03d}.mp3"
        output_path = os.path.join(output_folder, filename)
        await synthesize_to_file(text=line, output_path=output_path,
                                  voice=voice, rate=rate, volume=volume, pitch=pitch)
        output_files.append(output_path)
        if progress_callback:
            progress_callback(i + 1, len(lines))

    return output_files
