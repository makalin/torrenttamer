# TorrentTamer

**TorrentTamer** is a lightweight, terminal-based application for managing torrent files and magnet links. Built for efficiency and simplicity, it allows users to organize, monitor, and control torrent downloads directly from the command line. Perfect for power users who prefer a fast, text-based interface over GUI torrent clients.

## Features

### Core Features
- **Torrent File Management**: Add, remove, and organize .torrent files and magnet links.
- **Download Control**: Start, pause, resume, and stop torrent downloads.
- **Real-Time Monitoring**: Display download/upload speeds, progress, and peer information.
- **Cross-Platform**: Compatible with Windows, macOS, and Linux.
- **Lightweight**: Minimal resource usage, ideal for servers or low-spec systems.
- **Scriptable**: Easily integrate with shell scripts for automation.
- **Tracker Support**: Manage multiple trackers and prioritize them for optimal seeding/leeching.

### Advanced Features
- **Priority Management**: Set torrent and file priorities (0-7) for better control.
- **Sequential Download**: Enable sequential downloading for streaming media.
- **Super Seeding**: Optimize initial seeding for better distribution.
- **Force Recheck**: Verify data integrity of downloaded torrents.
- **Search & Filtering**: Search torrents by name and filter by status.
- **Export/Import**: Export torrent files and import them back.
- **Enhanced Monitoring**: Interactive monitoring with piece availability and peer information.
- **Session Statistics**: Detailed statistics and analytics.

### Automation Features
- **Scheduling**: Schedule torrent operations (start, stop, pause, resume) at specific times.
- **RSS Feeds**: Automatic downloads from RSS feeds with customizable filters.
- **Automation Rules**: Create custom automation rules based on conditions.
- **Backup & Restore**: Backup and restore torrent sessions.
- **Statistics Tracking**: Track download/upload statistics over time.

## Installation

### Prerequisites
- Python 3.8 or higher
- `pip` for installing dependencies
- `libtorrent` library for torrent handling

### Quick Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/makalin/torrenttamer.git
   cd torrenttamer
   ```

2. Run the installation script:
   - **Unix/macOS**: `./install.sh`
   - **Windows**: `install.bat`

3. Or install manually:
   ```bash
   pip install -r requirements.txt
   ```

### Manual Installation Steps
1. Install `libtorrent`:
   - On Ubuntu/Debian:
     ```bash
     sudo apt-get install python3-libtorrent
     ```
   - On macOS:
     ```bash
     brew install libtorrent-rasterbar
     ```
   - On Windows, use a pre-built wheel or follow the `libtorrent` documentation.

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python torrenttamer.py --help
   ```

## Usage

### Basic Commands

- **Add a torrent**:
  ```bash
  python torrenttamer.py add <path-to-torrent-file-or-magnet-link>
  python torrenttamer.py add "magnet:?xt=urn:btih:..." --priority 7 --sequential
  ```

- **List active torrents**:
  ```bash
  python torrenttamer.py list
  python torrenttamer.py list --status downloading
  ```

- **Control torrents**:
  ```bash
  python torrenttamer.py pause <torrent-id>
  python torrenttamer.py resume <torrent-id>
  python torrenttamer.py remove <torrent-id> --delete-data
  ```

- **Monitor downloads**:
  ```bash
  python torrenttamer.py monitor
  ```

### Advanced Commands

- **Priority Management**:
  ```bash
  python torrenttamer.py priority <torrent-id> <priority>
  python torrenttamer.py file-priority <torrent-id> <file-index> <priority>
  ```

- **Tracker Management**:
  ```bash
  python torrenttamer.py add-trackers <torrent-id> "http://tracker1.com" "http://tracker2.com"
  python torrenttamer.py remove-trackers <torrent-id> "http://bad-tracker.com"
  ```

- **Advanced Download Features**:
  ```bash
  python torrenttamer.py sequential <torrent-id> --enable
  python torrenttamer.py super-seeding <torrent-id> --enable
  python torrenttamer.py force-recheck <torrent-id>
  ```

- **Search and Information**:
  ```bash
  python torrenttamer.py search "ubuntu"
  python torrenttamer.py info <torrent-id>
  python torrenttamer.py stats
  ```

- **Export/Import**:
  ```bash
  python torrenttamer.py export <torrent-id> /path/to/output.torrent
  ```

### Advanced Features Usage

#### Scheduling
```python
from advanced_features import TorrentScheduler

scheduler = TorrentScheduler(torrent_manager)
scheduler.add_schedule('morning_start', 1, 'start', '09:00', 
                      ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'])
scheduler.start_scheduler()
```

#### RSS Feeds
```python
from advanced_features import RSSFeedManager

rss_manager = RSSFeedManager(torrent_manager, "~/Downloads")
rss_manager.add_feed('linux_iso', 'https://example.com/linux.rss')
rss_manager.add_filter('linux_iso', 'Ubuntu', priority=7)
rss_manager.start_rss_monitor()
```

#### Automation Rules
```python
from advanced_features import TorrentAutomation

automation = TorrentAutomation(torrent_manager)

def low_disk_space():
    return get_free_space() < 10 * 1024 * 1024 * 1024  # 10GB

def pause_all_torrents():
    for torrent_id in torrent_manager.get_torrents():
        torrent_manager.pause_torrent(torrent_id)

automation.add_rule('low_disk', low_disk_space, pause_all_torrents)
```

#### Statistics and Backup
```python
from advanced_features import TorrentStatistics, TorrentBackup

# Statistics
statistics = TorrentStatistics(torrent_manager)
statistics.update_stats()
daily_stats = statistics.get_daily_stats()

# Backup
backup = TorrentBackup(torrent_manager)
backup_file = backup.create_backup('my_backup')
```

## Configuration

TorrentTamer uses a configuration file (`config.ini`) for settings:

```ini
[Settings]
download_path = ~/Downloads
max_upload_speed = 500
max_download_speed = 0
max_connections = 200
enable_dht = true
enable_lsd = true
enable_upnp = true
auto_start = false
sequential_download = false
super_seeding = false
```

### Configuration Options
- `download_path`: Default download directory
- `max_upload_speed`: Upload speed limit in KB/s (0 = unlimited)
- `max_download_speed`: Download speed limit in KB/s (0 = unlimited)
- `max_connections`: Maximum number of connections
- `enable_dht`: Enable Distributed Hash Table
- `enable_lsd`: Enable Local Service Discovery
- `enable_upnp`: Enable UPnP port mapping
- `auto_start`: Automatically start added torrents
- `sequential_download`: Enable sequential download by default
- `super_seeding`: Enable super seeding by default

## Priority Levels

TorrentTamer supports 8 priority levels:
- **0**: Do Not Download
- **1**: Low
- **2**: Normal Low
- **3**: Normal
- **4**: Normal High
- **5**: High
- **6**: Very High
- **7**: Maximum

## Monitoring Features

The real-time monitor includes:
- **Basic Information**: Name, progress, speeds, peers, status, priority
- **Piece Availability**: Visual representation of downloaded pieces
- **Peer Information**: Detailed peer statistics and client information
- **Interactive Controls**: Press 'p' to toggle piece view, 'e' to toggle peer view

## Examples

### Basic Usage
```bash
# Add a torrent with high priority
python torrenttamer.py add "magnet:?xt=urn:btih:..." --priority 7

# List only downloading torrents
python torrenttamer.py list --status downloading

# Monitor with enhanced features
python torrenttamer.py monitor
```

### Advanced Usage
```bash
# Set file priority for streaming
python torrenttamer.py file-priority 1 0 7

# Enable sequential download for video files
python torrenttamer.py sequential 1 --enable

# Add additional trackers
python torrenttamer.py add-trackers 1 "http://tracker.opentrackr.org:1337/announce"

# Export torrent file
python torrenttamer.py export 1 exported.torrent
```

### Programmatic Usage
```python
from torrenttamer import TorrentTamer

app = TorrentTamer()

# Add torrent with custom settings
torrent_id = app.torrent_manager.add_torrent("magnet:...", priority=7, sequential=True)

# Set file priorities
app.torrent_manager.set_file_priority(torrent_id, 0, 7)

# Get detailed information
info = app.torrent_manager.get_torrent_peers(torrent_id)
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
- Advanced features inspired by modern torrent clients like qBittorrent and Transmission.
