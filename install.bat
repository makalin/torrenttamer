@echo off
REM TorrentTamer Installation Script for Windows

echo === TorrentTamer Installation ===
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is required but not installed.
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo ✓ Python found

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is required but not installed.
    echo Please install pip and try again.
    pause
    exit /b 1
)

echo ✓ pip found

REM Install libtorrent
echo Installing libtorrent...
pip install libtorrent

REM Install other dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo === Installation Complete ===
echo.
echo You can now use TorrentTamer with the following commands:
echo   python torrenttamer.py --help
echo   python torrenttamer.py add ^<torrent-file-or-magnet-link^>
echo   python torrenttamer.py list
echo   python torrenttamer.py monitor
echo.
echo For more information, see the README.md file.
pause 