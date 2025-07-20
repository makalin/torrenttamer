#!/usr/bin/env python3
"""
Example usage of TorrentTamer
This script demonstrates how to use TorrentTamer programmatically
"""

import time
from torrenttamer import TorrentTamer


def main():
    print("=== TorrentTamer Example Usage ===")
    print()
    
    # Initialize TorrentTamer
    print("Initializing TorrentTamer...")
    app = TorrentTamer()
    print("✓ TorrentTamer initialized successfully")
    print()
    
    # List current torrents
    print("Current torrents:")
    app.list_torrents()
    print()
    
    # Example: Add a torrent (commented out to avoid actual downloads)
    print("Example: Adding a torrent")
    print("To add a torrent, use:")
    print("  app.add_torrent('magnet:?xt=urn:btih:...')")
    print("  app.add_torrent('/path/to/file.torrent')")
    print()
    
    # Example: Monitor torrents (commented out to avoid blocking)
    print("Example: Monitoring torrents")
    print("To start monitoring, use:")
    print("  app.monitor_torrents()")
    print("  # Press Ctrl+C to stop")
    print()
    
    # Example: Control torrents
    print("Example: Controlling torrents")
    print("To pause a torrent: app.pause_torrent(torrent_id)")
    print("To resume a torrent: app.resume_torrent(torrent_id)")
    print("To remove a torrent: app.remove_torrent(torrent_id)")
    print("To get torrent info: app.info_torrent(torrent_id)")
    print()
    
    # Show configuration
    print("Current configuration:")
    for section in app.config.sections():
        print(f"[{section}]")
        for key, value in app.config[section].items():
            print(f"  {key} = {value}")
    print()
    
    print("=== Example completed ===")
    print("For more information, see the README.md file")


if __name__ == "__main__":
    main() 