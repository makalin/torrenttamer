#!/bin/bash

# TorrentTamer Installation Script

echo "=== TorrentTamer Installation ==="
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python 3.8 or higher is required. Found version $python_version"
    exit 1
fi

echo "✓ Python $python_version found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✓ pip3 found"

# Install libtorrent based on OS
echo "Installing libtorrent..."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v apt-get &> /dev/null; then
        echo "Detected Ubuntu/Debian system"
        sudo apt-get update
        sudo apt-get install -y python3-libtorrent
    elif command -v yum &> /dev/null; then
        echo "Detected CentOS/RHEL system"
        sudo yum install -y python3-libtorrent
    elif command -v dnf &> /dev/null; then
        echo "Detected Fedora system"
        sudo dnf install -y python3-libtorrent
    else
        echo "Warning: Could not detect package manager. Please install libtorrent manually."
        echo "You can try: pip3 install libtorrent"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command -v brew &> /dev/null; then
        echo "Detected macOS with Homebrew"
        brew install libtorrent-rasterbar
    else
        echo "Warning: Homebrew not found. Please install libtorrent manually."
        echo "You can try: pip3 install libtorrent"
    fi
else
    echo "Warning: Unsupported OS. Please install libtorrent manually."
    echo "You can try: pip3 install libtorrent"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Make the main script executable
chmod +x torrenttamer.py

echo
echo "=== Installation Complete ==="
echo
echo "You can now use TorrentTamer with the following commands:"
echo "  python3 torrenttamer.py --help"
echo "  python3 torrenttamer.py add <torrent-file-or-magnet-link>"
echo "  python3 torrenttamer.py list"
echo "  python3 torrenttamer.py monitor"
echo
echo "For more information, see the README.md file." 