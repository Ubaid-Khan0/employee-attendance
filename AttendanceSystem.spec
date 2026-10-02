# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the Employee Attendance System.
# Build with:  pyinstaller AttendanceSystem.spec
#
# Result: dist/AttendanceSystem/  -> a folder you can copy to any Windows
# laptop (no Python needed there). The .py source is compiled inside the
# executable, so your code stays hidden.

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# DeepFace ships model/deepscans data + OpenCV needs its own binaries;
# let PyInstaller's hooks handle cv2/tensorflow, but make sure deepface
# itself is fully bundled.
hidden_imports = (
    collect_submodules('deepface')
    + collect_submodules('tkinter')
    + [
        'cv2',
        'PIL',
        'PIL.ImageTk',
        'openpyxl',
        'sqlite3',
    ]
)

datas = (
    collect_data_files('deepface')
    # NOTE: database.db, known_faces/ and employee_reports/ are intentionally
    # NOT bundled. They live next to the exe at runtime (see paths.py), so
    # user data is editable/movable without rebuilding the app.
)

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
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
    [],
    exclude_binaries=True,
    name='AttendanceSystem',
    debug=False,            # no debug output in the shipped build
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,          # IMPORTANT: hides the black terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',      # uncomment if you add an icon file
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='AttendanceSystem',
)
