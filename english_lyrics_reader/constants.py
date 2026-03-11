"""Constants and sample data for English Lyrics Reader."""

APP_TITLE = "英文歌词朗读器"
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
MODE_ENGLISH_ONLY = "仅朗读英文"
MODE_ENGLISH_THEN_CHINESE = "先英文后中文"
MODE_SELECTED_LINE = "仅朗读当前选中行"

READING_MODES = [MODE_ENGLISH_ONLY, MODE_ENGLISH_THEN_CHINESE, MODE_SELECTED_LINE]

# Export modes
EXPORT_ALL = "导出全部"
EXPORT_SELECTED = "导出选中行"
EXPORT_PER_LINE = "逐行导出到文件夹"

EXPORT_MODES = [EXPORT_ALL, EXPORT_SELECTED, EXPORT_PER_LINE]

# Sample content
SAMPLE_ENGLISH = """Hiding from the rain and snow
Trying to forget but I won't let go
Looking at a crowded street
Listening to my own heart beat
So many people all around the world
Tell me where do I find someone like you girl
Take me to your heart, take me to your soul
Give me your hand before I'm old
Show me what love is, haven't got a clue
Show me that wonders can be true
They say nothing lasts forever
We're only here today
Love is now or never
Bring me far away
Take me to your heart, take me to your soul
Give me your hand and hold me
Show me what love is, be my guiding star
It's easy, take me to your heart"""

SAMPLE_CHINESE = """躲避着雨雪
试着去遗忘，但我不会放手
望着熙熙攘攘的街道
倾听着自己的心跳
世界上有那么多人
告诉我，哪里能找到像你一样的女孩
把我带进你的心，带进你的灵魂
趁我还未老去，给我你的手
告诉我什么是爱，我毫无头绪
让我看到奇迹可以成真
他们说没有什么是永恒的
我们只拥有今天
爱是此刻，否则永远不会来
带我去远方
把我带进你的心，带进你的灵魂
给我你的手，紧紧握住我
告诉我什么是爱，做我的指路星
很简单，把我带进你的心"""
