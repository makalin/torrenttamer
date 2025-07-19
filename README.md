# TorrentTamer

**TorrentTamer** is a lightweight, terminal-based application for managing torrent files and magnet links. Built for efficiency and simplicity, it allows users to organize, monitor, and control torrent downloads directly from the command line. Perfect for power users who prefer a fast, text-based interface over GUI torrent clients.

## Features

- **Torrent File Management**: Add, remove, and organize .torrent files and magnet links.
- **Download Control**: Start, pause, resume, and stop torrent downloads.
- **Real-Time Monitoring**: Display download/upload speeds, progress, and peer information.
- **Cross-Platform**: Compatible with Windows, macOS, and Linux.
- **Lightweight**: Minimal resource usage, ideal for servers or low-spec systems.
- **Scriptable**: Easily integrate with shell scripts for automation.
- **Tracker Support**: Manage multiple trackers and prioritize them for optimal seeding/leeching.

## Installation

### Prerequisites
- Python 3.8 or higher
- `pip` for installing dependencies
- `libtorrent` library for torrent handling

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/makalin/torrenttamer.git
   cd torrenttamer
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install `libtorrent`:
   - On Ubuntu/Debian:
     ```bash
     sudo apt-get install python3-libtorrent
     ```
   - On macOS:
     ```bash
     brew install libtorrent-rasterbar
     ```
   - On Windows, use a pre-built wheel or follow the `libtorrent` documentation.

4. Run the application:
   ```bash
   python torrenttamer.py --help
   ```

## Usage

TorrentTamer provides a simple command-line interface. Below are some common commands:

- **Add a torrent**:
  ```bash
  python torrenttamer.py add <path-to-torrent-file-or-magnet-link>
  ```
  Example:
  ```bash
  python torrenttamer.py add "magnet:?xt=urn:btih:..."
  ```

- **List active torrents**:
  ```bash
  python torrenttamer.py list
  ```

- **Pause a torrent**:
  ```bash
  python torrenttamer.py pause <torrent-id>
  ```

- **Resume a torrent**:
  ```bash
  python torrenttamer.py resume <torrent-id>
  ```

- **Remove a torrent**:
  ```bash
  python torrenttamer.py remove <torrent-id>
  ```

- **Monitor downloads**:
  ```bash
  python torrenttamer.py monitor
  ```

Run `python torrenttamer.py --help` for a full list of commands and options.

## Configuration

TorrentTamer uses a configuration file (`config.ini`) for settings like download directory, bandwidth limits, and default trackers. Edit the file in the project root:

```ini
[Settings]
download_path = ~/Downloads
max_upload_speed = 500  # KB/s
max_download_speed = 0  # 0 for unlimited
```

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

Please follow the [Code of Conduct](CODE_OF_CONDUCT.md) and ensure your code adheres to the project's style guidelines.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Built with [libtorrent](https://www.libtorrent.org/) for torrent handling.
- Inspired by the simplicity of command-line tools like `htop` and `tmux`.
