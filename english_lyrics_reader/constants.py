"""Constants and sample data for English Lyrics Reader."""

APP_TITLE = "English Lyrics Reader"
APP_VERSION = "1.0.0"
WINDOW_MIN_WIDTH = 1100
WINDOW_MIN_HEIGHT = 750

# Default TTS settings
DEFAULT_VOICE = "en-US-JennyNeural"
DEFAULT_SPEED = "+0%"
DEFAULT_VOLUME = "+0%"
DEFAULT_PITCH = "+0Hz"
DEFAULT_PAUSE_MS = 500

# Reading modes
MODE_ENGLISH_ONLY = "English Only"
MODE_ENGLISH_THEN_CHINESE = "English then Chinese"
MODE_SELECTED_LINE = "Selected Line Only"

READING_MODES = [MODE_ENGLISH_ONLY, MODE_ENGLISH_THEN_CHINESE, MODE_SELECTED_LINE]

# Export modes
EXPORT_ALL = "Export All"
EXPORT_SELECTED = "Export Selected Line"
EXPORT_PER_LINE = "Export Per-Line Files"

EXPORT_MODES = [EXPORT_ALL, EXPORT_SELECTED, EXPORT_PER_LINE]

# Sample content
SAMPLE_ENGLISH = """I'm holding on your rope, Got me ten feet off the ground
And I'm hearin what you say but I just can't make a sound
You tell me that you need me
Then you go and cut me down, but wait
You tell me that you're sorry
Didn't think I'd turn around, and say
It's too late to apologize, it's too late"""

SAMPLE_CHINESE = """我紧握着你给的绳索，让我悬在离地十英尺的高空
我听到了你说的话，却发不出任何声音
你告诉我你需要我
然后你又把我推开，但是等等
你告诉我你很抱歉
没想到我会转身说
道歉已经太迟了，太迟了"""
