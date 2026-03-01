# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for RecoveryTron."""

import sys
import os

block_cipher = None

a = Analysis(
    ['../app.py'],
    pathex=[os.path.abspath('..')],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'bip_utils',
        'core',
        'core.bip39_words',
        'core.checksum',
        'core.constraints',
        'core.tron_derive',
        'core.matcher',
        'core.worker',
        'ui',
        'ui.main_window',
        'ui.mnemonic_grid',
        'ui.candidates_panel',
        'ui.results_table',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RecoveryTron',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
