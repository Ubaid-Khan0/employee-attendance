@echo off
REM ============================================================
REM  Build script - run this on YOUR Windows laptop (one time).
REM  Output: dist\AttendanceSystem\AttendanceSystem.exe
REM ============================================================

REM 1. Make sure you use the SAME Python where your libraries are installed
python -m pip install --upgrade pyinstaller

REM 2. Clean previous builds
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist

REM 3. Build the exe (code is compiled inside - no .py files shipped)
pyinstaller AttendanceSystem.spec --noconfirm

REM 4. Copy the data folders next to the exe so the app finds them
xcopy /i /e /y known_faces       dist\AttendanceSystem\known_faces
copy /y database.db              dist\AttendanceSystem\database.db
if not exist dist\AttendanceSystem\employee_reports mkdir dist\AttendanceSystem\employee_reports

echo.
echo ============================================================
echo  DONE. Now zip the whole "dist\AttendanceSystem" folder and
echo  copy it to the other laptop. No Python needed there.
echo ============================================================
pause
