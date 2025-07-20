#!/usr/bin/env python3
"""
TorrentTamer - A lightweight, terminal-based torrent manager
"""

import argparse
import asyncio
import configparser
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import libtorrent as lt

from torrent_manager import TorrentManager
from torrent_monitor import TorrentMonitor
from utils import format_size, format_speed, get_torrent_info


class TorrentTamer:
    def __init__(self):
        self.config = self._load_config()
        self.torrent_manager = TorrentManager(self.config)
        self.monitor = TorrentMonitor(self.torrent_manager)

    def _load_config(self) -> configparser.ConfigParser:
        """Load configuration from config.ini"""
        config = configparser.ConfigParser()
        config_file = Path("config.ini")
        
        if config_file.exists():
            config.read(config_file)
        else:
            # Create default config
            config['Settings'] = {
                'download_path': str(Path.home() / 'Downloads'),
                'max_upload_speed': '500',
                'max_download_speed': '0',
                'max_connections': '200',
                'enable_dht': 'true',
                'enable_lsd': 'true',
                'enable_upnp': 'true',
                'auto_start': 'false',
                'sequential_download': 'false',
                'super_seeding': 'false'
            }
            with open(config_file, 'w') as f:
                config.write(f)
        
        return config

    def add_torrent(self, torrent_path: str, priority: int = 5, sequential: bool = False) -> None:
        """Add a torrent file or magnet link"""
        try:
            torrent_id = self.torrent_manager.add_torrent(torrent_path, priority, sequential)
            print(f"✓ Torrent added successfully with ID: {torrent_id}")
        except Exception as e:
            print(f"✗ Error adding torrent: {e}")
            sys.exit(1)

    def list_torrents(self, filter_status: str = None) -> None:
        """List all active torrents with optional filtering"""
        torrents = self.torrent_manager.get_torrents()
        
        if not torrents:
            print("No active torrents found.")
            return
        
        # Filter torrents if specified
        if filter_status:
            filtered_torrents = {}
            for torrent_id, torrent in torrents.items():
                status = torrent.status()
                state = str(status.state).split('.')[-1].replace('_', ' ').title()
                if filter_status.lower() in state.lower():
                    filtered_torrents[torrent_id] = torrent
            torrents = filtered_torrents
            
            if not torrents:
                print(f"No torrents found with status: {filter_status}")
                return
        
        print(f"{'ID':<4} {'Name':<40} {'Progress':<10} {'Size':<12} {'Status':<10} {'Priority':<8}")
        print("-" * 90)
        
        for torrent_id, torrent in torrents.items():
            status = torrent.status()
            name = torrent.name()[:39] + "..." if len(torrent.name()) > 40 else torrent.name()
            progress = f"{status.progress * 100:.1f}%"
            size = format_size(status.total_wanted)
            state = str(status.state).split('.')[-1].replace('_', ' ').title()
            priority = torrent.get_priority()
            
            print(f"{torrent_id:<4} {name:<40} {progress:<10} {size:<12} {state:<10} {priority:<8}")

    def pause_torrent(self, torrent_id: int) -> None:
        """Pause a torrent"""
        try:
            self.torrent_manager.pause_torrent(torrent_id)
            print(f"✓ Torrent {torrent_id} paused successfully")
        except Exception as e:
            print(f"✗ Error pausing torrent: {e}")
            sys.exit(1)

    def resume_torrent(self, torrent_id: int) -> None:
        """Resume a torrent"""
        try:
            self.torrent_manager.resume_torrent(torrent_id)
            print(f"✓ Torrent {torrent_id} resumed successfully")
        except Exception as e:
            print(f"✗ Error resuming torrent: {e}")
            sys.exit(1)

    def remove_torrent(self, torrent_id: int, delete_data: bool = False) -> None:
        """Remove a torrent"""
        try:
            self.torrent_manager.remove_torrent(torrent_id, delete_data)
            print(f"✓ Torrent {torrent_id} removed successfully")
        except Exception as e:
            print(f"✗ Error removing torrent: {e}")
            sys.exit(1)

    def monitor_torrents(self) -> None:
        """Start real-time monitoring"""
        try:
            self.monitor.start()
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
        except Exception as e:
            print(f"✗ Error during monitoring: {e}")
            sys.exit(1)

    def info_torrent(self, torrent_id: int) -> None:
        """Show detailed information about a torrent"""
        try:
            torrent = self.torrent_manager.get_torrent(torrent_id)
            if not torrent:
                print(f"✗ Torrent with ID {torrent_id} not found")
                return
            
            info = get_torrent_info(torrent)
            print(f"\n=== Torrent Information ===")
            print(f"Name: {info['name']}")
            print(f"Size: {info['size']}")
            print(f"Progress: {info['progress']:.1f}%")
            print(f"Download Speed: {info['download_speed']}")
            print(f"Upload Speed: {info['upload_speed']}")
            print(f"Peers: {info['peers']}")
            print(f"Seeds: {info['seeds']}")
            print(f"Status: {info['status']}")
            print(f"Save Path: {info['save_path']}")
            print(f"Priority: {torrent.get_priority()}")
            
            if info['files']:
                print(f"\nFiles:")
                for file_info in info['files']:
                    print(f"  {file_info['name']} ({file_info['size']}) - Priority: {file_info['priority']}")
            
        except Exception as e:
            print(f"✗ Error getting torrent info: {e}")
            sys.exit(1)

    def set_priority(self, torrent_id: int, priority: int) -> None:
        """Set torrent priority (0-7)"""
        try:
            self.torrent_manager.set_priority(torrent_id, priority)
            print(f"✓ Torrent {torrent_id} priority set to {priority}")
        except Exception as e:
            print(f"✗ Error setting priority: {e}")
            sys.exit(1)

    def set_file_priority(self, torrent_id: int, file_index: int, priority: int) -> None:
        """Set file priority within a torrent"""
        try:
            self.torrent_manager.set_file_priority(torrent_id, file_index, priority)
            print(f"✓ File {file_index} priority set to {priority}")
        except Exception as e:
            print(f"✗ Error setting file priority: {e}")
            sys.exit(1)

    def add_trackers(self, torrent_id: int, trackers: List[str]) -> None:
        """Add trackers to a torrent"""
        try:
            self.torrent_manager.add_trackers(torrent_id, trackers)
            print(f"✓ Added {len(trackers)} trackers to torrent {torrent_id}")
        except Exception as e:
            print(f"✗ Error adding trackers: {e}")
            sys.exit(1)

    def remove_trackers(self, torrent_id: int, tracker_urls: List[str]) -> None:
        """Remove trackers from a torrent"""
        try:
            self.torrent_manager.remove_trackers(torrent_id, tracker_urls)
            print(f"✓ Removed {len(tracker_urls)} trackers from torrent {torrent_id}")
        except Exception as e:
            print(f"✗ Error removing trackers: {e}")
            sys.exit(1)

    def force_recheck(self, torrent_id: int) -> None:
        """Force recheck of torrent data"""
        try:
            self.torrent_manager.force_recheck(torrent_id)
            print(f"✓ Force recheck started for torrent {torrent_id}")
        except Exception as e:
            print(f"✗ Error starting recheck: {e}")
            sys.exit(1)

    def set_sequential_download(self, torrent_id: int, enabled: bool) -> None:
        """Enable/disable sequential download"""
        try:
            self.torrent_manager.set_sequential_download(torrent_id, enabled)
            status = "enabled" if enabled else "disabled"
            print(f"✓ Sequential download {status} for torrent {torrent_id}")
        except Exception as e:
            print(f"✗ Error setting sequential download: {e}")
            sys.exit(1)

    def set_super_seeding(self, torrent_id: int, enabled: bool) -> None:
        """Enable/disable super seeding"""
        try:
            self.torrent_manager.set_super_seeding(torrent_id, enabled)
            status = "enabled" if enabled else "disabled"
            print(f"✓ Super seeding {status} for torrent {torrent_id}")
        except Exception as e:
            print(f"✗ Error setting super seeding: {e}")
            sys.exit(1)

    def export_torrent(self, torrent_id: int, output_path: str) -> None:
        """Export torrent file"""
        try:
            self.torrent_manager.export_torrent(torrent_id, output_path)
            print(f"✓ Torrent exported to {output_path}")
        except Exception as e:
            print(f"✗ Error exporting torrent: {e}")
            sys.exit(1)

    def get_session_stats(self) -> None:
        """Display session statistics"""
        try:
            stats = self.torrent_manager.get_session_stats()
            print("\n=== Session Statistics ===")
            print(f"Total Download: {format_size(stats['total_download'])}")
            print(f"Total Upload: {format_size(stats['total_upload'])}")
            print(f"Download Rate: {format_speed(stats['download_rate'])}")
            print(f"Upload Rate: {format_speed(stats['upload_rate'])}")
            print(f"Active Peers: {stats['num_peers']}")
            print(f"Active Torrents: {stats['num_torrents']}")
        except Exception as e:
            print(f"✗ Error getting session stats: {e}")
            sys.exit(1)

    def search_torrents(self, query: str) -> None:
        """Search torrents by name"""
        try:
            results = self.torrent_manager.search_torrents(query)
            if not results:
                print(f"No torrents found matching '{query}'")
                return
            
            print(f"\n=== Search Results for '{query}' ===")
            print(f"{'ID':<4} {'Name':<50} {'Progress':<10} {'Status':<12}")
            print("-" * 80)
            
            for torrent_id, torrent in results.items():
                status = torrent.status()
                name = torrent.name()[:49] + "..." if len(torrent.name()) > 50 else torrent.name()
                progress = f"{status.progress * 100:.1f}%"
                state = str(status.state).split('.')[-1].replace('_', ' ').title()
                
                print(f"{torrent_id:<4} {name:<50} {progress:<10} {state:<12}")
                
        except Exception as e:
            print(f"✗ Error searching torrents: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="TorrentTamer - A lightweight, terminal-based torrent manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python torrenttamer.py add "magnet:?xt=urn:btih:..."
  python torrenttamer.py add /path/to/file.torrent --priority 7
  python torrenttamer.py list
  python torrenttamer.py list --status downloading
  python torrenttamer.py pause 1
  python torrenttamer.py resume 1
  python torrenttamer.py remove 1
  python torrenttamer.py monitor
  python torrenttamer.py info 1
  python torrenttamer.py priority 1 7
  python torrenttamer.py file-priority 1 0 7
  python torrenttamer.py add-trackers 1 "http://tracker1.com" "http://tracker2.com"
  python torrenttamer.py force-recheck 1
  python torrenttamer.py sequential 1 --enable
  python torrenttamer.py super-seeding 1 --enable
  python torrenttamer.py export 1 /path/to/output.torrent
  python torrenttamer.py stats
  python torrenttamer.py search "ubuntu"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a torrent file or magnet link')
    add_parser.add_argument('torrent', help='Path to torrent file or magnet link')
    add_parser.add_argument('--priority', type=int, default=5, choices=range(8),
                          help='Torrent priority (0-7, default: 5)')
    add_parser.add_argument('--sequential', action='store_true',
                          help='Enable sequential download')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all active torrents')
    list_parser.add_argument('--status', help='Filter by status (e.g., downloading, seeding)')
    
    # Pause command
    pause_parser = subparsers.add_parser('pause', help='Pause a torrent')
    pause_parser.add_argument('torrent_id', type=int, help='Torrent ID')
    
    # Resume command
    resume_parser = subparsers.add_parser('resume', help='Resume a torrent')
    resume_parser.add_argument('torrent_id', type=int, help='Torrent ID')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove a torrent')
    remove_parser.add_argument('torrent_id', type=int, help='Torrent ID')
    remove_parser.add_argument('--delete-data', action='store_true', 
                              help='Also delete downloaded data')
    
    # Monitor command
    subparsers.add_parser('monitor', help='Start real-time monitoring')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show detailed torrent information')
    info_parser.add_argument('torrent_id', type=int, help='Torrent ID')
    
    # Priority command
    priority_parser = subparsers.add_parser('priority', help='Set torrent priority')
    priority_parser.add_argument('torrent_id', type=int, help='Torrent ID')
    priority_parser.add_argument('priority', type=int, choices=range(8), help='Priority (0-7)')
    
    # File priority command
    file_priority_parser = subparsers.add_parser('file-priority', help='Set file priority')
    file_priority_parser.add_argument('torrent_id', type=int, help='Torrent ID')
    file_priority_parser.add_argument('file_index', type=int, help='File index')
    file_priority_parser.add_argument('priority', type=int, choices=range(8), help='Priority (0-7)')
    
    # Add trackers command
    add_trackers_parser = subparsers.add_parser('add-trackers', help='Add trackers to torrent')
    add_trackers_parser.add_argument('torrent_id', type=int, help='Torrent ID')
    add_trackers_parser.add_argument('trackers', nargs='+', help='Tracker URLs')
    
    # Remove trackers command
    remove_trackers_parser = subparsers.add_parser('remove-trackers', help='Remove trackers from torrent')
    remove_trackers_parser.add_argument('torrent_id', type=int, help='Torrent ID')
    remove_trackers_parser.add_argument('trackers', nargs='+', help='Tracker URLs to remove')
    
    # Force recheck command
    recheck_parser = subparsers.add_parser('force-recheck', help='Force recheck torrent data')
    recheck_parser.add_argument('torrent_id', type=int, help='Torrent ID')
    
    # Sequential download command
    sequential_parser = subparsers.add_parser('sequential', help='Enable/disable sequential download')
    sequential_parser.add_argument('torrent_id', type=int, help='Torrent ID')
    sequential_parser.add_argument('--enable', action='store_true', help='Enable sequential download')
    sequential_parser.add_argument('--disable', action='store_true', help='Disable sequential download')
    
    # Super seeding command
    super_seeding_parser = subparsers.add_parser('super-seeding', help='Enable/disable super seeding')
    super_seeding_parser.add_argument('torrent_id', type=int, help='Torrent ID')
    super_seeding_parser.add_argument('--enable', action='store_true', help='Enable super seeding')
    super_seeding_parser.add_argument('--disable', action='store_true', help='Disable super seeding')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export torrent file')
    export_parser.add_argument('torrent_id', type=int, help='Torrent ID')
    export_parser.add_argument('output_path', help='Output file path')
    
    # Stats command
    subparsers.add_parser('stats', help='Show session statistics')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search torrents by name')
    search_parser.add_argument('query', help='Search query')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        app = TorrentTamer()
        
        if args.command == 'add':
            app.add_torrent(args.torrent, args.priority, args.sequential)
        elif args.command == 'list':
            app.list_torrents(args.status)
        elif args.command == 'pause':
            app.pause_torrent(args.torrent_id)
        elif args.command == 'resume':
            app.resume_torrent(args.torrent_id)
        elif args.command == 'remove':
            app.remove_torrent(args.torrent_id, args.delete_data)
        elif args.command == 'monitor':
            app.monitor_torrents()
        elif args.command == 'info':
            app.info_torrent(args.torrent_id)
        elif args.command == 'priority':
            app.set_priority(args.torrent_id, args.priority)
        elif args.command == 'file-priority':
            app.set_file_priority(args.torrent_id, args.file_index, args.priority)
        elif args.command == 'add-trackers':
            app.add_trackers(args.torrent_id, args.trackers)
        elif args.command == 'remove-trackers':
            app.remove_trackers(args.torrent_id, args.trackers)
        elif args.command == 'force-recheck':
            app.force_recheck(args.torrent_id)
        elif args.command == 'sequential':
            enabled = args.enable if args.enable else not args.disable
            app.set_sequential_download(args.torrent_id, enabled)
        elif args.command == 'super-seeding':
            enabled = args.enable if args.enable else not args.disable
            app.set_super_seeding(args.torrent_id, enabled)
        elif args.command == 'export':
            app.export_torrent(args.torrent_id, args.output_path)
        elif args.command == 'stats':
            app.get_session_stats()
        elif args.command == 'search':
            app.search_torrents(args.query)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 