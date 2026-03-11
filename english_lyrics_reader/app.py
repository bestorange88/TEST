"""Main application module for English Lyrics Reader."""

import json
import os
import tempfile
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Optional

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from english_lyrics_reader.constants import (
    APP_TITLE,
    APP_VERSION,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
    DEFAULT_VOICE,
    DEFAULT_PAUSE_MS,
    MODE_ENGLISH_ONLY,
    MODE_ENGLISH_THEN_CHINESE,
    MODE_SELECTED_LINE,
    READING_MODES,
    EXPORT_ALL,
    EXPORT_SELECTED,
    EXPORT_PER_LINE,
    EXPORT_MODES,
    SAMPLE_ENGLISH,
    SAMPLE_CHINESE,
)
from english_lyrics_reader.tts_engine import (
    get_voices_sync,
    get_english_voices,
    get_chinese_voices,
    synthesize_to_file_sync,
)


class EnglishLyricsReader:
    """Main application class for English Lyrics Reader."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{APP_TITLE} v{APP_VERSION}")
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.root.geometry(f"{WINDOW_MIN_WIDTH}x{WINDOW_MIN_HEIGHT}")

        # State variables
        self.is_reading = False
        self.is_paused = False
        self._stop_event = threading.Event()
        self.current_line_index = 0
        self.reading_thread: Optional[threading.Thread] = None
        self.loop_current_line = False

        # Voice lists
        self.all_voices: List[dict] = []
        self.english_voice_names: List[str] = []
        self.chinese_voice_names: List[str] = []

        # Temp dir for audio files
        self.temp_dir = tempfile.mkdtemp(prefix="lyrics_reader_")

        # Initialize pygame mixer
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
            except Exception:
                pass

        # Build UI
        self._create_styles()
        self._build_ui()
        self._load_voices_async()

    def _create_styles(self):
        """Create ttk styles for the application."""
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Status.TLabel", font=("Segoe UI", 10))
        style.configure("Highlight.TLabel", font=("Segoe UI", 10, "bold"),
                         foreground="#0066CC")
        style.configure("Action.TButton", padding=(10, 5))
        style.configure("Control.TButton", padding=(8, 4))

    def _build_ui(self):
        """Build the main UI layout."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text=f"{APP_TITLE}",
            style="Title.TLabel",
        )
        title_label.pack(pady=(0, 10))

        # Create a PanedWindow for resizable layout
        paned = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Top frame: Text input area
        top_frame = ttk.Frame(paned)
        paned.add(top_frame, weight=3)

        self._build_text_area(top_frame)

        # Bottom frame: Settings, Controls, Status
        bottom_frame = ttk.Frame(paned)
        paned.add(bottom_frame, weight=2)

        self._build_settings_area(bottom_frame)
        self._build_control_area(bottom_frame)
        self._build_status_area(bottom_frame)

    def _build_text_area(self, parent: ttk.Frame):
        """Build the text input area with English and Chinese text boxes."""
        text_frame = ttk.LabelFrame(parent, text="Lyrics Input", padding=5)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # Configure grid
        text_frame.columnconfigure(0, weight=1)
        text_frame.columnconfigure(1, weight=1)
        text_frame.rowconfigure(1, weight=1)

        # English label and text
        en_label = ttk.Label(text_frame, text="English Lyrics:")
        en_label.grid(row=0, column=0, sticky=tk.W, padx=(5, 2))

        en_text_frame = ttk.Frame(text_frame)
        en_text_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=(5, 2), pady=2)
        en_text_frame.rowconfigure(0, weight=1)
        en_text_frame.columnconfigure(0, weight=1)

        self.en_text = tk.Text(
            en_text_frame, wrap=tk.WORD, font=("Consolas", 11),
            undo=True, height=10
        )
        self.en_text.grid(row=0, column=0, sticky=tk.NSEW)
        en_scroll = ttk.Scrollbar(en_text_frame, orient=tk.VERTICAL,
                                   command=self.en_text.yview)
        en_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.en_text.configure(yscrollcommand=en_scroll.set)

        # Chinese label and text
        cn_label = ttk.Label(text_frame, text="Chinese Translation:")
        cn_label.grid(row=0, column=1, sticky=tk.W, padx=(2, 5))

        cn_text_frame = ttk.Frame(text_frame)
        cn_text_frame.grid(row=1, column=1, sticky=tk.NSEW, padx=(2, 5), pady=2)
        cn_text_frame.rowconfigure(0, weight=1)
        cn_text_frame.columnconfigure(0, weight=1)

        self.cn_text = tk.Text(
            cn_text_frame, wrap=tk.WORD, font=("Microsoft YaHei", 11),
            undo=True, height=10
        )
        self.cn_text.grid(row=0, column=0, sticky=tk.NSEW)
        cn_scroll = ttk.Scrollbar(cn_text_frame, orient=tk.VERTICAL,
                                   command=self.cn_text.yview)
        cn_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.cn_text.configure(yscrollcommand=cn_scroll.set)

        # Configure highlight tags
        self.en_text.tag_configure("highlight", background="#FFFF99",
                                    foreground="#000000")
        self.cn_text.tag_configure("highlight", background="#FFFF99",
                                    foreground="#000000")

    def _build_settings_area(self, parent: ttk.Frame):
        """Build the parameter settings area."""
        settings_frame = ttk.LabelFrame(parent, text="Settings", padding=5)
        settings_frame.pack(fill=tk.X, pady=(0, 5))

        # Row 1: Voice, Speed
        row1 = ttk.Frame(settings_frame)
        row1.pack(fill=tk.X, pady=2)

        # Voice selection
        ttk.Label(row1, text="Voice:").pack(side=tk.LEFT, padx=(5, 2))
        self.voice_var = tk.StringVar(value=DEFAULT_VOICE)
        self.voice_combo = ttk.Combobox(
            row1, textvariable=self.voice_var, state="readonly", width=30
        )
        self.voice_combo.pack(side=tk.LEFT, padx=(0, 15))

        # Speed
        ttk.Label(row1, text="Speed:").pack(side=tk.LEFT, padx=(5, 2))
        self.speed_var = tk.IntVar(value=0)
        self.speed_scale = ttk.Scale(
            row1, from_=-50, to=50, variable=self.speed_var,
            orient=tk.HORIZONTAL, length=120,
            command=lambda v: self.speed_var.set(int(float(v)))
        )
        self.speed_scale.pack(side=tk.LEFT, padx=(0, 2))
        self.speed_label = ttk.Label(row1, text="0%", width=6)
        self.speed_label.pack(side=tk.LEFT, padx=(0, 15))
        self.speed_var.trace_add("write", self._update_speed_label)

        # Volume
        ttk.Label(row1, text="Volume:").pack(side=tk.LEFT, padx=(5, 2))
        self.volume_var = tk.IntVar(value=0)
        self.volume_scale = ttk.Scale(
            row1, from_=-50, to=50, variable=self.volume_var,
            orient=tk.HORIZONTAL, length=120,
            command=lambda v: self.volume_var.set(int(float(v)))
        )
        self.volume_scale.pack(side=tk.LEFT, padx=(0, 2))
        self.volume_label = ttk.Label(row1, text="0%", width=6)
        self.volume_label.pack(side=tk.LEFT, padx=(0, 15))
        self.volume_var.trace_add("write", self._update_volume_label)

        # Pitch
        ttk.Label(row1, text="Pitch:").pack(side=tk.LEFT, padx=(5, 2))
        self.pitch_var = tk.IntVar(value=0)
        self.pitch_scale = ttk.Scale(
            row1, from_=-50, to=50, variable=self.pitch_var,
            orient=tk.HORIZONTAL, length=120,
            command=lambda v: self.pitch_var.set(int(float(v)))
        )
        self.pitch_scale.pack(side=tk.LEFT, padx=(0, 2))
        self.pitch_label = ttk.Label(row1, text="0Hz", width=6)
        self.pitch_label.pack(side=tk.LEFT)
        self.pitch_var.trace_add("write", self._update_pitch_label)

        # Row 2: Reading mode, Pause time, Loop
        row2 = ttk.Frame(settings_frame)
        row2.pack(fill=tk.X, pady=2)

        ttk.Label(row2, text="Reading Mode:").pack(side=tk.LEFT, padx=(5, 2))
        self.mode_var = tk.StringVar(value=MODE_ENGLISH_ONLY)
        mode_combo = ttk.Combobox(
            row2, textvariable=self.mode_var, values=READING_MODES,
            state="readonly", width=22
        )
        mode_combo.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(row2, text="Pause (ms):").pack(side=tk.LEFT, padx=(5, 2))
        self.pause_var = tk.IntVar(value=DEFAULT_PAUSE_MS)
        pause_spin = ttk.Spinbox(
            row2, from_=0, to=5000, increment=100,
            textvariable=self.pause_var, width=8
        )
        pause_spin.pack(side=tk.LEFT, padx=(0, 15))

        self.loop_var = tk.BooleanVar(value=False)
        loop_check = ttk.Checkbutton(
            row2, text="Loop Current Line", variable=self.loop_var
        )
        loop_check.pack(side=tk.LEFT, padx=(5, 15))

        # Chinese voice (for bilingual mode)
        ttk.Label(row2, text="Chinese Voice:").pack(side=tk.LEFT, padx=(5, 2))
        self.cn_voice_var = tk.StringVar(value="zh-CN-XiaoxiaoNeural")
        self.cn_voice_combo = ttk.Combobox(
            row2, textvariable=self.cn_voice_var, state="readonly", width=25
        )
        self.cn_voice_combo.pack(side=tk.LEFT, padx=(0, 5))

    def _build_control_area(self, parent: ttk.Frame):
        """Build the control buttons area."""
        control_frame = ttk.LabelFrame(parent, text="Controls", padding=5)
        control_frame.pack(fill=tk.X, pady=(0, 5))

        # Row 1: File operations
        file_row = ttk.Frame(control_frame)
        file_row.pack(fill=tk.X, pady=2)

        ttk.Button(file_row, text="Load Sample",
                    command=self.load_sample, style="Action.TButton"
                    ).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_row, text="Import TXT",
                    command=self.import_txt, style="Action.TButton"
                    ).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_row, text="Save TXT",
                    command=self.save_txt, style="Action.TButton"
                    ).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_row, text="Save JSON",
                    command=self.save_json, style="Action.TButton"
                    ).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_row, text="Clear Text",
                    command=self.clear_text, style="Action.TButton"
                    ).pack(side=tk.LEFT, padx=2)

        # Row 2: Playback controls
        play_row = ttk.Frame(control_frame)
        play_row.pack(fill=tk.X, pady=2)

        self.start_btn = ttk.Button(
            play_row, text="Start Reading",
            command=self.start_reading, style="Action.TButton"
        )
        self.start_btn.pack(side=tk.LEFT, padx=2)

        self.pause_btn = ttk.Button(
            play_row, text="Pause",
            command=self.pause_reading, style="Control.TButton",
            state=tk.DISABLED
        )
        self.pause_btn.pack(side=tk.LEFT, padx=2)

        self.resume_btn = ttk.Button(
            play_row, text="Resume",
            command=self.resume_reading, style="Control.TButton",
            state=tk.DISABLED
        )
        self.resume_btn.pack(side=tk.LEFT, padx=2)

        self.stop_btn = ttk.Button(
            play_row, text="Stop",
            command=self.stop_reading, style="Control.TButton",
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=2)

        ttk.Button(play_row, text="Preview Current Line",
                    command=self.preview_current_line, style="Action.TButton"
                    ).pack(side=tk.LEFT, padx=2)

        # Row 3: Export controls
        export_row = ttk.Frame(control_frame)
        export_row.pack(fill=tk.X, pady=2)

        ttk.Label(export_row, text="Export Mode:").pack(side=tk.LEFT, padx=(5, 2))
        self.export_mode_var = tk.StringVar(value=EXPORT_ALL)
        export_combo = ttk.Combobox(
            export_row, textvariable=self.export_mode_var,
            values=EXPORT_MODES, state="readonly", width=20
        )
        export_combo.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(export_row, text="Export Audio",
                    command=self.export_audio, style="Action.TButton"
                    ).pack(side=tk.LEFT, padx=2)

    def _build_status_area(self, parent: ttk.Frame):
        """Build the status display area."""
        status_frame = ttk.LabelFrame(parent, text="Status", padding=5)
        status_frame.pack(fill=tk.X, pady=(0, 5))

        # Line info
        info_row = ttk.Frame(status_frame)
        info_row.pack(fill=tk.X, pady=2)

        ttk.Label(info_row, text="Current Line:").pack(side=tk.LEFT, padx=(5, 2))
        self.line_num_label = ttk.Label(info_row, text="0 / 0", style="Status.TLabel")
        self.line_num_label.pack(side=tk.LEFT, padx=(0, 15))

        # Current English content
        en_row = ttk.Frame(status_frame)
        en_row.pack(fill=tk.X, pady=1)
        ttk.Label(en_row, text="EN:").pack(side=tk.LEFT, padx=(5, 2))
        self.current_en_label = ttk.Label(
            en_row, text="", style="Highlight.TLabel", wraplength=800
        )
        self.current_en_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Current Chinese content
        cn_row = ttk.Frame(status_frame)
        cn_row.pack(fill=tk.X, pady=1)
        ttk.Label(cn_row, text="CN:").pack(side=tk.LEFT, padx=(5, 2))
        self.current_cn_label = ttk.Label(
            cn_row, text="", style="Highlight.TLabel", wraplength=800
        )
        self.current_cn_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Progress bar
        progress_row = ttk.Frame(status_frame)
        progress_row.pack(fill=tk.X, pady=2)
        ttk.Label(progress_row, text="Progress:").pack(side=tk.LEFT, padx=(5, 2))
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_row, variable=self.progress_var,
            maximum=100, length=400
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        # Status message
        msg_row = ttk.Frame(status_frame)
        msg_row.pack(fill=tk.X, pady=1)
        ttk.Label(msg_row, text="Status:").pack(side=tk.LEFT, padx=(5, 2))
        self.status_msg_label = ttk.Label(
            msg_row, text="Ready", style="Status.TLabel"
        )
        self.status_msg_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # ─── Label Update Helpers ───────────────────────────────────────

    def _update_speed_label(self, *_args):
        val = self.speed_var.get()
        sign = "+" if val >= 0 else ""
        self.speed_label.configure(text=f"{sign}{val}%")

    def _update_volume_label(self, *_args):
        val = self.volume_var.get()
        sign = "+" if val >= 0 else ""
        self.volume_label.configure(text=f"{sign}{val}%")

    def _update_pitch_label(self, *_args):
        val = self.pitch_var.get()
        sign = "+" if val >= 0 else ""
        self.pitch_label.configure(text=f"{sign}{val}Hz")

    # ─── TTS Parameter Helpers ──────────────────────────────────────

    def _get_rate_str(self) -> str:
        val = self.speed_var.get()
        sign = "+" if val >= 0 else ""
        return f"{sign}{val}%"

    def _get_volume_str(self) -> str:
        val = self.volume_var.get()
        sign = "+" if val >= 0 else ""
        return f"{sign}{val}%"

    def _get_pitch_str(self) -> str:
        val = self.pitch_var.get()
        sign = "+" if val >= 0 else ""
        return f"{sign}{val}Hz"

    # ─── Voice Loading ──────────────────────────────────────────────

    def _load_voices_async(self):
        """Load voices in a background thread."""
        self._set_status("Loading voices from edge-tts...")

        def _load():
            try:
                self.all_voices = get_voices_sync()
                self.english_voice_names = get_english_voices(self.all_voices)
                self.chinese_voice_names = get_chinese_voices(self.all_voices)
                self.root.after(0, self._populate_voice_combos)
            except Exception as err:
                msg = f"Failed to load voices: {err}"
                self.root.after(0, lambda m=msg: self._set_status(m))

        thread = threading.Thread(target=_load, daemon=True)
        thread.start()

    def _populate_voice_combos(self):
        """Populate voice combo boxes after loading."""
        if self.english_voice_names:
            self.voice_combo["values"] = self.english_voice_names
            if DEFAULT_VOICE in self.english_voice_names:
                self.voice_var.set(DEFAULT_VOICE)
            else:
                self.voice_var.set(self.english_voice_names[0])

        if self.chinese_voice_names:
            self.cn_voice_combo["values"] = self.chinese_voice_names
            if "zh-CN-XiaoxiaoNeural" in self.chinese_voice_names:
                self.cn_voice_var.set("zh-CN-XiaoxiaoNeural")
            else:
                self.cn_voice_var.set(self.chinese_voice_names[0])

        self._set_status(
            f"Voices loaded: {len(self.english_voice_names)} EN, "
            f"{len(self.chinese_voice_names)} CN"
        )

    # ─── Text Helpers ───────────────────────────────────────────────

    def _get_english_lines(self) -> List[str]:
        """Get English lines from text widget, stripping empty lines."""
        raw = self.en_text.get("1.0", tk.END).strip()
        if not raw:
            return []
        lines = [line.strip() for line in raw.split("\n")]
        # Remove trailing empty lines but keep internal ones
        while lines and not lines[-1]:
            lines.pop()
        return lines

    def _get_chinese_lines(self) -> List[str]:
        """Get Chinese lines from text widget."""
        raw = self.cn_text.get("1.0", tk.END).strip()
        if not raw:
            return []
        lines = [line.strip() for line in raw.split("\n")]
        while lines and not lines[-1]:
            lines.pop()
        return lines

    def _get_aligned_lines(self):
        """Get aligned English and Chinese lines."""
        en_lines = self._get_english_lines()
        cn_lines = self._get_chinese_lines()

        # Pad Chinese lines if shorter
        while len(cn_lines) < len(en_lines):
            cn_lines.append("")

        return en_lines, cn_lines

    def _highlight_line(self, line_index: int):
        """Highlight the specified line in both text widgets."""
        # Remove previous highlights
        self.en_text.tag_remove("highlight", "1.0", tk.END)
        self.cn_text.tag_remove("highlight", "1.0", tk.END)

        en_lines = self._get_english_lines()
        cn_lines = self._get_chinese_lines()

        if 0 <= line_index < len(en_lines):
            start = f"{line_index + 1}.0"
            end = f"{line_index + 1}.end"
            self.en_text.tag_add("highlight", start, end)
            self.en_text.see(start)

        if 0 <= line_index < len(cn_lines):
            start = f"{line_index + 1}.0"
            end = f"{line_index + 1}.end"
            self.cn_text.tag_add("highlight", start, end)
            self.cn_text.see(start)

    def _get_selected_line_index(self) -> int:
        """Get the line index where the cursor is in the English text widget."""
        try:
            cursor_pos = self.en_text.index(tk.INSERT)
            line_num = int(cursor_pos.split(".")[0])
            return line_num - 1  # Convert to 0-indexed
        except (tk.TclError, ValueError):
            return 0

    # ─── Status Helper ──────────────────────────────────────────────

    def _set_status(self, msg: str):
        """Update the status message."""
        self.status_msg_label.configure(text=msg)

    def _update_line_info(self, current: int, total: int,
                          en_text: str = "", cn_text: str = ""):
        """Update the current line display."""
        self.line_num_label.configure(text=f"{current} / {total}")
        self.current_en_label.configure(text=en_text)
        self.current_cn_label.configure(text=cn_text)
        if total > 0:
            self.progress_var.set((current / total) * 100)
        else:
            self.progress_var.set(0)

    # ─── Button State Management ────────────────────────────────────

    def _set_reading_state(self, reading: bool):
        """Update button states based on reading status."""
        if reading:
            self.start_btn.configure(state=tk.DISABLED)
            self.pause_btn.configure(state=tk.NORMAL)
            self.resume_btn.configure(state=tk.DISABLED)
            self.stop_btn.configure(state=tk.NORMAL)
        else:
            self.start_btn.configure(state=tk.NORMAL)
            self.pause_btn.configure(state=tk.DISABLED)
            self.resume_btn.configure(state=tk.DISABLED)
            self.stop_btn.configure(state=tk.DISABLED)

    # ─── File Operations ────────────────────────────────────────────

    def load_sample(self):
        """Load sample lyrics."""
        self.en_text.delete("1.0", tk.END)
        self.cn_text.delete("1.0", tk.END)
        self.en_text.insert("1.0", SAMPLE_ENGLISH.strip())
        self.cn_text.insert("1.0", SAMPLE_CHINESE.strip())
        self._set_status("Sample text loaded.")

    def import_txt(self):
        """Import lyrics from a TXT file."""
        filepath = filedialog.askopenfilename(
            title="Import TXT File",
            filetypes=[("Text Files", "*.txt"), ("JSON Files", "*.json"),
                       ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            if filepath.endswith(".json"):
                data = json.loads(content)
                en_text = data.get("english", "")
                cn_text = data.get("chinese", "")
            else:
                # Check for separator markers
                if "---" in content or "===" in content:
                    parts = content.split("---") if "---" in content else content.split("===")
                    en_text = parts[0].strip()
                    cn_text = parts[1].strip() if len(parts) > 1 else ""
                else:
                    en_text = content.strip()
                    cn_text = ""

            self.en_text.delete("1.0", tk.END)
            self.cn_text.delete("1.0", tk.END)
            self.en_text.insert("1.0", en_text)
            if cn_text:
                self.cn_text.insert("1.0", cn_text)

            self._set_status(f"Imported: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import file:\n{e}")

    def save_txt(self):
        """Save lyrics to a TXT file."""
        filepath = filedialog.asksaveasfilename(
            title="Save as TXT",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            en_text = self.en_text.get("1.0", tk.END).strip()
            cn_text = self.cn_text.get("1.0", tk.END).strip()

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(en_text)
                if cn_text:
                    f.write("\n---\n")
                    f.write(cn_text)

            self._set_status(f"Saved: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file:\n{e}")

    def save_json(self):
        """Save lyrics to a JSON project file."""
        filepath = filedialog.asksaveasfilename(
            title="Save as JSON",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            en_lines = self._get_english_lines()
            cn_lines = self._get_chinese_lines()

            data = {
                "english": "\n".join(en_lines),
                "chinese": "\n".join(cn_lines),
                "english_lines": en_lines,
                "chinese_lines": cn_lines,
                "settings": {
                    "voice": self.voice_var.get(),
                    "chinese_voice": self.cn_voice_var.get(),
                    "speed": self.speed_var.get(),
                    "volume": self.volume_var.get(),
                    "pitch": self.pitch_var.get(),
                    "mode": self.mode_var.get(),
                    "pause_ms": self.pause_var.get(),
                }
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self._set_status(f"Saved: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file:\n{e}")

    def clear_text(self):
        """Clear all text areas."""
        self.en_text.delete("1.0", tk.END)
        self.cn_text.delete("1.0", tk.END)
        self._update_line_info(0, 0)
        self._set_status("Text cleared.")

    # ─── Playback Operations ────────────────────────────────────────

    def _play_audio_file(self, filepath: str,
                          stop_event: threading.Event = None):
        """Play an audio file using pygame mixer.

        Args:
            filepath: Path to the audio file to play.
            stop_event: Per-session Event; when set, playback stops.
        """
        if not PYGAME_AVAILABLE:
            self._set_status("pygame not available for audio playback")
            return
        if stop_event is None:
            stop_event = self._stop_event

        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            # Wait for playback to finish
            # Use a flag to track if we are in a paused state to avoid
            # exiting the loop when get_busy() returns False due to pause.
            while True:
                if stop_event.is_set():
                    pygame.mixer.music.stop()
                    return
                if self.is_paused:
                    # While paused, just wait without checking get_busy
                    time.sleep(0.1)
                    continue
                if not pygame.mixer.music.get_busy():
                    break
                time.sleep(0.05)
        except Exception as err:
            msg = f"Playback error: {err}"
            self.root.after(0, lambda m=msg: self._set_status(m))

    def _synthesize_and_play_line(self, text: str, voice: str,
                                    stop_event: threading.Event = None
                                    ) -> bool:
        """Synthesize a line and play it. Returns False if stopped.

        Args:
            text: Text to synthesize.
            voice: Voice name to use.
            stop_event: Per-session Event; when set, synthesis/playback stops.
        """
        if not text.strip():
            return True
        if stop_event is None:
            stop_event = self._stop_event
        if stop_event.is_set():
            return False

        try:
            # Generate temp file
            temp_file = os.path.join(
                self.temp_dir,
                f"line_{int(time.time() * 1000)}.mp3"
            )
            synthesize_to_file_sync(
                text=text,
                output_path=temp_file,
                voice=voice,
                rate=self._get_rate_str(),
                volume=self._get_volume_str(),
                pitch=self._get_pitch_str(),
            )

            if stop_event.is_set():
                return False

            self._play_audio_file(temp_file, stop_event)

            # Clean up temp file
            try:
                os.remove(temp_file)
            except OSError:
                pass

            return not stop_event.is_set()
        except Exception as err:
            msg = f"TTS Error: {err}"
            self.root.after(0, lambda m=msg: self._set_status(m))
            return not stop_event.is_set()

    def _reading_worker(self, start_index: int = 0,
                         single_line: bool = False,
                         stop_event: threading.Event = None):
        """Background worker for reading lyrics line by line.

        Args:
            start_index: The line index to start reading from.
            single_line: If True, only read the single line at start_index.
            stop_event: Per-session Event; when set, reading stops.
        """
        if stop_event is None:
            stop_event = self._stop_event

        en_lines, cn_lines = self._get_aligned_lines()
        total = len(en_lines)

        if total == 0:
            self.root.after(0, lambda: self._set_status("No text to read."))
            self.root.after(0, lambda: self._set_reading_state(False))
            return

        mode = self.mode_var.get()
        pause_ms = self.pause_var.get()

        end_index = start_index + 1 if single_line else total

        i = start_index
        while i < end_index and not stop_event.is_set():
            # Wait while paused
            while self.is_paused and not stop_event.is_set():
                time.sleep(0.1)

            if stop_event.is_set():
                break

            self.current_line_index = i
            en_line = en_lines[i]
            cn_line = cn_lines[i] if i < len(cn_lines) else ""

            # Update UI
            self.root.after(0, lambda idx=i: self._highlight_line(idx))
            self.root.after(0, lambda ei=i+1, t=total, e=en_line, c=cn_line:
                            self._update_line_info(ei, t, e, c))
            self.root.after(0, lambda e=en_line:
                            self._set_status(f"Reading: {e[:60]}..."))

            # Read English line
            if en_line.strip():
                voice = self.voice_var.get()
                if not self._synthesize_and_play_line(
                    en_line, voice, stop_event
                ):
                    break

            # Read Chinese line if mode requires
            if mode == MODE_ENGLISH_THEN_CHINESE and cn_line.strip():
                if stop_event.is_set():
                    break
                cn_voice = self.cn_voice_var.get()
                if not self._synthesize_and_play_line(
                    cn_line, cn_voice, stop_event
                ):
                    break

            # Handle loop mode
            if self.loop_var.get():
                # Stay on current line
                if not stop_event.is_set():
                    time.sleep(pause_ms / 1000.0)
                continue

            # Pause between lines
            if not stop_event.is_set() and i < end_index - 1:
                time.sleep(pause_ms / 1000.0)

            i += 1

        # Reading complete
        self.is_reading = False
        self.root.after(0, lambda: self._set_reading_state(False))
        if not stop_event.is_set():
            self.root.after(0, lambda: self._set_status("Reading complete."))
            self.root.after(0, lambda: self.progress_var.set(100))
        else:
            self.root.after(0, lambda: self._set_status("Reading stopped."))

    def start_reading(self):
        """Start reading lyrics."""
        en_lines = self._get_english_lines()
        if not en_lines:
            self._set_status("No English text to read.")
            return

        mode = self.mode_var.get()
        if mode == MODE_SELECTED_LINE:
            # Only read the single selected line
            idx = self._get_selected_line_index()
            if idx >= len(en_lines):
                idx = 0
            self._start_reading_from(idx, single_line=True)
            return

        # Start from selected line or beginning
        start_idx = self._get_selected_line_index()
        if start_idx >= len(en_lines):
            start_idx = 0

        self._start_reading_from(start_idx)

    def _stop_any_playback(self):
        """Stop any ongoing reading or preview before starting new playback.

        Sets the current session's stop event so the running thread will
        terminate. Even if the thread outlives the join timeout, it holds
        a reference to its own (now-set) event, so it will still stop
        independently of any new session's event.
        """
        self._stop_event.set()
        self.is_paused = False
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        if self.reading_thread and self.reading_thread.is_alive():
            self.reading_thread.join(timeout=2.0)
        self.is_reading = False

    def _start_reading_from(self, start_index: int,
                              single_line: bool = False):
        """Start reading from a specific line index."""
        self._stop_any_playback()
        # Create a NEW stop event for this session. The old thread (if still
        # alive) holds a reference to the previous (now-set) event, so it
        # will see the stop signal regardless of this new event.
        stop_event = threading.Event()
        self._stop_event = stop_event
        self.is_reading = True
        self.is_paused = False
        self._set_reading_state(True)

        self.reading_thread = threading.Thread(
            target=self._reading_worker,
            args=(start_index, single_line, stop_event),
            daemon=True
        )
        self.reading_thread.start()

    def pause_reading(self):
        """Pause the current reading."""
        if self.is_reading:
            self.is_paused = True
            self.pause_btn.configure(state=tk.DISABLED)
            self.resume_btn.configure(state=tk.NORMAL)
            if PYGAME_AVAILABLE:
                try:
                    pygame.mixer.music.pause()
                except Exception:
                    pass
            self._set_status("Paused.")

    def resume_reading(self):
        """Resume the paused reading."""
        if self.is_reading and self.is_paused:
            self.is_paused = False
            self.pause_btn.configure(state=tk.NORMAL)
            self.resume_btn.configure(state=tk.DISABLED)
            if PYGAME_AVAILABLE:
                try:
                    pygame.mixer.music.unpause()
                except Exception:
                    pass
            self._set_status("Resumed.")

    def stop_reading(self):
        """Stop the current reading."""
        self._stop_event.set()
        self.is_paused = False
        self.is_reading = False
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        self._set_reading_state(False)
        self.en_text.tag_remove("highlight", "1.0", tk.END)
        self.cn_text.tag_remove("highlight", "1.0", tk.END)
        self._set_status("Stopped.")

    def preview_current_line(self):
        """Preview (read aloud) the current selected line."""
        en_lines = self._get_english_lines()
        if not en_lines:
            self._set_status("No text to preview.")
            return

        # Stop any ongoing playback first
        self._stop_any_playback()

        idx = self._get_selected_line_index()
        if idx >= len(en_lines):
            idx = 0

        en_line = en_lines[idx]
        cn_lines = self._get_chinese_lines()
        cn_line = cn_lines[idx] if idx < len(cn_lines) else ""

        self._highlight_line(idx)
        self._update_line_info(idx + 1, len(en_lines), en_line, cn_line)
        self._set_status(f"Previewing line {idx + 1}...")

        # Create a new stop event for this preview session
        stop_event = threading.Event()
        self._stop_event = stop_event
        self.is_reading = True
        self._set_reading_state(True)

        def _preview():
            voice = self.voice_var.get()
            self._synthesize_and_play_line(en_line, voice, stop_event)
            mode = self.mode_var.get()
            if mode == MODE_ENGLISH_THEN_CHINESE and cn_line.strip():
                cn_voice = self.cn_voice_var.get()
                self._synthesize_and_play_line(cn_line, cn_voice, stop_event)
            self.is_reading = False
            self.root.after(0, lambda: self._set_reading_state(False))
            self.root.after(0, lambda: self._set_status("Preview complete."))

        self.reading_thread = threading.Thread(target=_preview, daemon=True)
        self.reading_thread.start()

    # ─── Export Operations ──────────────────────────────────────────

    def export_audio(self):
        """Export audio based on selected export mode."""
        export_mode = self.export_mode_var.get()
        en_lines = self._get_english_lines()

        if not en_lines:
            self._set_status("No text to export.")
            return

        if export_mode == EXPORT_ALL:
            self._export_all_lines(en_lines)
        elif export_mode == EXPORT_SELECTED:
            self._export_selected_line(en_lines)
        elif export_mode == EXPORT_PER_LINE:
            self._export_per_line(en_lines)

    def _export_all_lines(self, en_lines: List[str]):
        """Export all lines as a single MP3 file."""
        filepath = filedialog.asksaveasfilename(
            title="Export All as MP3",
            defaultextension=".mp3",
            filetypes=[("MP3 Files", "*.mp3"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        self._set_status("Exporting all lines...")

        def _export():
            try:
                # Combine all lines into one text
                combined_text = ". ".join(
                    line for line in en_lines if line.strip()
                )
                synthesize_to_file_sync(
                    text=combined_text,
                    output_path=filepath,
                    voice=self.voice_var.get(),
                    rate=self._get_rate_str(),
                    volume=self._get_volume_str(),
                    pitch=self._get_pitch_str(),
                )
                self.root.after(0, lambda: self._set_status(
                    f"Exported: {os.path.basename(filepath)}"
                ))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Export Complete",
                    f"Audio exported to:\n{filepath}"
                ))
            except Exception as err:
                msg = f"Export error: {err}"
                self.root.after(0, lambda m=msg: self._set_status(m))
                detail = f"Failed to export:\n{err}"
                self.root.after(0, lambda d=detail: messagebox.showerror(
                    "Export Error", d
                ))

        thread = threading.Thread(target=_export, daemon=True)
        thread.start()

    def _export_selected_line(self, en_lines: List[str]):
        """Export the selected line as MP3."""
        idx = self._get_selected_line_index()
        if idx >= len(en_lines):
            idx = 0

        line = en_lines[idx]
        if not line.strip():
            self._set_status("Selected line is empty.")
            return

        filepath = filedialog.asksaveasfilename(
            title=f"Export Line {idx + 1} as MP3",
            defaultextension=".mp3",
            initialfile=f"line_{idx + 1:03d}.mp3",
            filetypes=[("MP3 Files", "*.mp3"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        self._set_status(f"Exporting line {idx + 1}...")

        def _export():
            try:
                synthesize_to_file_sync(
                    text=line,
                    output_path=filepath,
                    voice=self.voice_var.get(),
                    rate=self._get_rate_str(),
                    volume=self._get_volume_str(),
                    pitch=self._get_pitch_str(),
                )
                self.root.after(0, lambda: self._set_status(
                    f"Exported line {idx + 1}: {os.path.basename(filepath)}"
                ))
            except Exception as err:
                msg = f"Export error: {err}"
                self.root.after(0, lambda m=msg: self._set_status(m))

        thread = threading.Thread(target=_export, daemon=True)
        thread.start()

    def _export_per_line(self, en_lines: List[str]):
        """Export each line as a separate MP3 file in a folder."""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if not folder:
            return

        self._set_status("Exporting per-line audio files...")

        def _export():
            try:
                total = len(en_lines)
                exported = 0
                for i, line in enumerate(en_lines):
                    if not line.strip():
                        continue
                    filename = f"line_{i + 1:03d}.mp3"
                    output_path = os.path.join(folder, filename)
                    synthesize_to_file_sync(
                        text=line,
                        output_path=output_path,
                        voice=self.voice_var.get(),
                        rate=self._get_rate_str(),
                        volume=self._get_volume_str(),
                        pitch=self._get_pitch_str(),
                    )
                    exported += 1
                    self.root.after(0, lambda c=exported, t=total:
                                    self._set_status(
                                        f"Exported {c}/{t} lines..."
                                    ))
                    self.root.after(0, lambda c=exported, t=total:
                                    self.progress_var.set(
                                        (c / t) * 100
                                    ))

                self.root.after(0, lambda: self._set_status(
                    f"Exported {exported} files to: {folder}"
                ))
                self.root.after(0, lambda: messagebox.showinfo(
                    "Export Complete",
                    f"Exported {exported} audio files to:\n{folder}"
                ))
            except Exception as err:
                msg = f"Export error: {err}"
                self.root.after(0, lambda m=msg: self._set_status(m))
                detail = f"Failed to export:\n{err}"
                self.root.after(0, lambda d=detail: messagebox.showerror(
                    "Export Error", d
                ))

        thread = threading.Thread(target=_export, daemon=True)
        thread.start()

    # ─── Cleanup ────────────────────────────────────────────────────

    def cleanup(self):
        """Clean up resources on exit."""
        self._stop_event.set()
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.quit()
            except Exception:
                pass
        # Clean temp directory
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass
