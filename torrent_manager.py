#!/usr/bin/env python3
"""
Torrent Manager - Core torrent handling functionality
"""

import configparser
import os
import time
from pathlib import Path
from typing import Dict, Optional, List

import libtorrent as lt


class TorrentManager:
    def __init__(self, config: configparser.ConfigParser):
        self.config = config
        self.session = self._create_session()
        self.torrents: Dict[int, lt.torrent_handle] = {}
        self.next_torrent_id = 1

    def _create_session(self) -> lt.session:
        """Create and configure libtorrent session"""
        # Create session with default settings
        session = lt.session()
        
        # Set bandwidth limits
        max_upload = self.config.getint('Settings', 'max_upload_speed', fallback=500) * 1024
        max_download = self.config.getint('Settings', 'max_download_speed', fallback=0) * 1024
        
        if max_upload > 0:
            session.set_upload_rate_limit(max_upload)
        if max_download > 0:
            session.set_download_rate_limit(max_download)
        
        return session

    def add_torrent(self, torrent_path: str, priority: int = 5, sequential: bool = False) -> int:
        """Add a torrent file or magnet link"""
        download_path = Path(self.config.get('Settings', 'download_path', fallback='~/Downloads'))
        download_path = download_path.expanduser()
        download_path.mkdir(parents=True, exist_ok=True)
        
        params = lt.add_magnet_link_params()
        
        if torrent_path.startswith('magnet:'):
            # Handle magnet link
            params.url = torrent_path
            params.save_path = str(download_path)
        else:
            # Handle torrent file
            if not os.path.exists(torrent_path):
                raise FileNotFoundError(f"Torrent file not found: {torrent_path}")
            
            info = lt.torrent_info(torrent_path)
            params.ti = info
            params.save_path = str(download_path)
        
        torrent_handle = self.session.add_torrent(params)
        torrent_id = self.next_torrent_id
        self.torrents[torrent_id] = torrent_handle
        self.next_torrent_id += 1
        
        # Set priority
        torrent_handle.set_priority(priority)
        
        # Set sequential download if requested
        if sequential:
            torrent_handle.set_sequential_download(True)
        
        # Auto-start if configured
        if self.config.getboolean('Settings', 'auto_start', fallback=False):
            torrent_handle.resume()
        
        return torrent_id

    def get_torrent(self, torrent_id: int) -> Optional[lt.torrent_handle]:
        """Get torrent handle by ID"""
        return self.torrents.get(torrent_id)

    def get_torrents(self) -> Dict[int, lt.torrent_handle]:
        """Get all active torrents"""
        return self.torrents.copy()

    def pause_torrent(self, torrent_id: int) -> None:
        """Pause a torrent"""
        torrent = self.get_torrent(torrent_id)
        if not torrent:
            raise ValueError(f"Torrent with ID {torrent_id} not found")
        
        torrent.pause()

    def resume_torrent(self, torrent_id: int) -> None:
        """Resume a torrent"""
        torrent = self.get_torrent(torrent_id)
        if not torrent:
            raise ValueError(f"Torrent with ID {torrent_id} not found")
        
        torrent.resume()

    def remove_torrent(self, torrent_id: int, delete_data: bool = False) -> None:
        """Remove a torrent"""
        torrent = self.get_torrent(torrent_id)
        if not torrent:
            raise ValueError(f"Torrent with ID {torrent_id} not found")
        
        self.session.remove_torrent(torrent, delete_data)
        del self.torrents[torrent_id]

    def set_priority(self, torrent_id: int, priority: int) -> None:
        """Set torrent priority (0-7)"""
        torrent = self.get_torrent(torrent_id)
        if not torrent:
            raise ValueError(f"Torrent with ID {torrent_id} not found")
        
        if not 0 <= priority <= 7:
            raise ValueError("Priority must be between 0 and 7")
        
        torrent.set_priority(priority)

    def set_file_priority(self, torrent_id: int, file_index: int, priority: int) -> None:
        """Set file priority within a torrent"""
        torrent = self.get_torrent(torrent_id)
        if not torrent:
            raise ValueError(f"Torrent with ID {torrent_id} not found")
        
        if not 0 <= priority <= 7:
            raise ValueError("Priority must be between 0 and 7")
        
        torrent.file_priority(file_index, priority)

    def add_trackers(self, torrent_id: int, trackers: List[str]) -> None:
        """Add trackers to a torrent"""
        torrent = self.get_torrent(torrent_id)
        if not torrent:
            raise ValueError(f"Torrent with ID {torrent_id} not found")
        
        for tracker in trackers:
            torrent.add_tracker(tracker)

    def remove_trackers(self, torrent_id: int, tracker_urls: List[str]) -> None:
        """Remove trackers from a torrent"""
        torrent = self.get_torrent(torrent_id)
        if not torrent:
            raise ValueError(f"Torrent with ID {torrent_id} not found")
        
        # Get current trackers
        current_trackers = torrent.get_trackers()
        
        # Create new tracker list excluding the ones to remove
        new_trackers = []
        for tracker in current_trackers:
            if tracker['url'] not in tracker_urls:
                new_trackers.append(tracker['url'])
        
        # Replace all trackers with the filtered list
        torrent.replace_trackers(new_trackers)

    def force_recheck(self, torrent_id: int) -> None:
        """Force recheck of torrent data"""
        torrent = self.get_torrent(torrent_id)
        if not torrent:
            raise ValueError(f"Torrent with ID {torrent_id} not found")
        
        torrent.force_recheck()

    def set_sequential_download(self, torrent_id: int, enabled: bool) -> None:
        """Enable/disable sequential download"""
        torrent = self.get_torrent(torrent_id)
        if not torrent:
            raise ValueError(f"Torrent with ID {torrent_id} not found")
        
        torrent.set_sequential_download(enabled)

    def set_super_seeding(self, torrent_id: int, enabled: bool) -> None:
        """Enable/disable super seeding"""
        torrent = self.get_torrent(torrent_id)
        if not torrent:
            raise ValueError(f"Torrent with ID {torrent_id} not found")
        
        torrent.set_super_seeding(enabled)

    def export_torrent(self, torrent_id: int, output_path: str) -> None:
        """Export torrent file"""
        torrent = self.get_torrent(torrent_id)
        if not torrent:
            raise ValueError(f"Torrent with ID {torrent_id} not found")
        
        info = torrent.get_torrent_info()
        if not info:
            raise ValueError("Torrent info not available")
        
        # Create torrent file
        torrent_file = lt.create_torrent(info)
        
        # Write to file
        with open(output_path, 'wb') as f:
            f.write(lt.bencode(torrent_file.generate()))

    def search_torrents(self, query: str) -> Dict[int, lt.torrent_handle]:
        """Search torrents by name"""
        results = {}
        query_lower = query.lower()
        
        for torrent_id, torrent in self.torrents.items():
            name = torrent.name().lower()
            if query_lower in name:
                results[torrent_id] = torrent
        
        return results

    def get_session_stats(self) -> Dict:
        """Get session statistics"""
        # Calculate totals from all torrents
        total_download = 0
        total_upload = 0
        download_rate = 0
        upload_rate = 0
        num_peers = 0
        
        for torrent in self.torrents.values():
            status = torrent.status()
            total_download += status.total_download
            total_upload += status.total_upload
            download_rate += status.download_rate
            upload_rate += status.upload_rate
            num_peers += status.num_peers
        
        return {
            'total_download': total_download,
            'total_upload': total_upload,
            'download_rate': download_rate,
            'upload_rate': upload_rate,
            'num_peers': num_peers,
            'num_torrents': len(self.torrents)
        }

    def get_torrent_peers(self, torrent_id: int) -> List[Dict]:
        """Get peer information for a torrent"""
        torrent = self.get_torrent(torrent_id)
        if not torrent:
            raise ValueError(f"Torrent with ID {torrent_id} not found")
        
        peers = torrent.get_peer_info()
        peer_list = []
        
        for peer in peers:
            peer_list.append({
                'ip': peer.ip,
                'port': peer.port,
                'client': peer.client,
                'progress': peer.progress,
                'download_rate': peer.download_rate,
                'upload_rate': peer.upload_rate,
                'flags': peer.flags
            })
        
        return peer_list

    def get_torrent_pieces(self, torrent_id: int) -> List[bool]:
        """Get piece availability for a torrent"""
        torrent = self.get_torrent(torrent_id)
        if not torrent:
            raise ValueError(f"Torrent with ID {torrent_id} not found")
        
        status = torrent.status()
        return status.pieces

    def set_download_limit(self, torrent_id: int, limit: int) -> None:
        """Set download speed limit for a torrent (KB/s)"""
        torrent = self.get_torrent(torrent_id)
        if not torrent:
            raise ValueError(f"Torrent with ID {torrent_id} not found")
        
        torrent.set_download_limit(limit * 1024)

    def set_upload_limit(self, torrent_id: int, limit: int) -> None:
        """Set upload speed limit for a torrent (KB/s)"""
        torrent = self.get_torrent(torrent_id)
        if not torrent:
            raise ValueError(f"Torrent with ID {torrent_id} not found")
        
        torrent.set_upload_limit(limit * 1024)

    def move_storage(self, torrent_id: int, new_path: str) -> None:
        """Move torrent storage to new location"""
        torrent = self.get_torrent(torrent_id)
        if not torrent:
            raise ValueError(f"Torrent with ID {torrent_id} not found")
        
        torrent.move_storage(new_path)

    def cleanup(self) -> None:
        """Cleanup resources"""
        for torrent in self.torrents.values():
            self.session.remove_torrent(torrent, False)
        self.torrents.clear() 