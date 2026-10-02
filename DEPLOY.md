# Deploying the app with your code hidden

Your project is a **Tkinter desktop app** (not a website), so "hide the code,
run the frontend on another laptop" = **compile it into an executable**.

## Recommended: PyInstaller (one-file folder build)

### On YOUR laptop (build machine, Windows)
1. `pip install pyinstaller`
2. Double-click `build_exe.bat` (or run it in a terminal)
3. Wait until it finishes -> you get `dist\AttendanceSystem\`

### On the OTHER laptop (target machine)
1. Zip the whole `dist\AttendanceSystem` folder and copy it over
2. Unzip anywhere, double-click **AttendanceSystem.exe**
3. No Python, no pip, no source files needed there

Folder layout on the target laptop:
```
AttendanceSystem/
├── AttendanceSystem.exe   <- your compiled code (hidden)
├── database.db            <- attendance data
├── known_faces/           <- registered employee faces
└── employee_reports/      <- exported Excel files
```

## Important notes
- **Build on Windows if the target is Windows.** PyInstaller cannot
  cross-compile (a Linux/macOS build only runs on Linux/macOS).
- The path logic (`paths.py`) puts `database.db`, `known_faces/` and
  `employee_reports/` **next to the exe**, so data survives app updates and
  you can ship pre-loaded faces/data with the build.
- `console=False` in the spec hides the black terminal window.
- Heavy libs (deepface/tensorflow/opencv) make the exe large (~1-2 GB) and
  the first face-recognition run may be slow while models load. This is normal.
- Smart antivirus sometimes flags unsigned PyInstaller exes; if that happens,
  add an exclusion or code-sign the exe.

## Reality check about "hiding code"
- The .exe contains compiled `.pyc` bytecode, not plain .py files. A casual
  user cannot read or edit your code, but a determined person *can* decompile
  Python bytecode. PyInstaller is obfuscation-by-packaging, not encryption.
- For stronger protection: use a commercial packer/pyarmor (`pyarmor` +
  PyInstaller), or move sensitive logic (e.g., recognition) to a server API
  so it never ships to the other laptop at all.

## Alternative (no compiling): client-server
Keep this Python app running on YOUR laptop as a Flask/socket server and let
the other laptop open a browser UI pointing at it. Your code never leaves
your machine. More setup, but truly hidden code.
