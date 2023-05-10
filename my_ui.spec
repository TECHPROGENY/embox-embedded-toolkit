# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['my_ui.py'],
    pathex=[],
    binaries=[('/home/nikhil/.local/lib/python3.10/site-packages/PyQt6/Qt6/lib/', '.')],
    datas=[('files/*', '.')],
    hiddenimports=['paho-mqtt', 'qt_material', 'requests', 'numpy'],
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
    name='my_ui',
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
