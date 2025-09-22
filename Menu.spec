# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Menu.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\\\Users\\\\WPOSS BGA 634K\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python313\\\\Lib\\\\site-packages\\\\ttkbootstrap', 'ttkbootstrap')],
    hiddenimports=['tkinter', 'ttkbootstrap', 'binascii', 'gzip'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Menu',
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
    icon=['quill.ico'],
)
