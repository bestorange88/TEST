============================================
  English Lyrics Reader - Windows EXE Build
============================================

1. Install Python 3.11+ (https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. Open Command Prompt (cmd) in this folder

3. Install dependencies:
   pip install -r requirements.txt
   pip install pyinstaller

4. Build EXE (Method 1 - using build script):
   python build_exe.py

5. Build EXE (Method 2 - manual):
   pyinstaller --name=EnglishLyricsReader --onefile --windowed --hidden-import=edge_tts --hidden-import=pygame --hidden-import=asyncio --hidden-import=aiohttp --collect-all=edge_tts run.py

6. The EXE file will be in the "dist" folder:
   dist\EnglishLyricsReader.exe

7. Run directly without building EXE:
   python run.py

NOTE: The app requires internet connection for TTS (edge-tts uses Microsoft Edge online TTS service).
