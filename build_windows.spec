# -*- mode: python ; coding: utf-8 -*-
"""
Windows用 PyInstaller ビルド設定
使い方: pyinstaller build_windows.spec
"""

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'winocr',
        'winsdk',
        'deep_translator',
        'deep_translator.google',
        'cv2',
        'numpy',
        'mss',
        'mss.windows',
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Live AreaTranslator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # GUIアプリなのでコンソール非表示
    icon=None,        # アイコンがあれば 'icon.ico' を指定
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Live AreaTranslator',
)
