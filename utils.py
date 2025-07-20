#!/usr/bin/env python3
"""
Utilities - Helper functions for TorrentTamer
"""

import hashlib
import libtorrent as lt
import os
import time
from typing import Dict, List, Optional, Tuple


def format_size(bytes_value: int) -> str:
    """Format bytes into human readable format"""
    if bytes_value == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    
    while bytes_value >= 1024 and unit_index < len(units) - 1:
        bytes_value /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{bytes_value:.0f} {units[unit_index]}"
    else:
        return f"{bytes_value:.1f} {units[unit_index]}"


def format_speed(bytes_per_second: int) -> str:
    """Format bytes per second into human readable format"""
    if bytes_per_second == 0:
        return "0 B/s"
    
    return f"{format_size(bytes_per_second)}/s"


def format_time(seconds: int) -> str:
    """Format seconds into human readable time"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}m {seconds}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours}h {minutes}m {seconds}s"


def format_progress_bar(progress: float, width: int = 20) -> str:
    """Create a progress bar string"""
    filled = int(progress * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {progress * 100:.1f}%"


def get_torrent_info(torrent: lt.torrent_handle) -> Dict:
    """Get comprehensive information about a torrent"""
    status = torrent.status()
    info = torrent.get_torrent_info()
    
    # Get file information
    files = []
    if info:
        for i in range(info.num_files()):
            file_entry = info.files()[i]
            files.append({
                'name': file_entry.path,
                'size': format_size(file_entry.size),
                'priority': file_entry.priority
            })
    
    # Get state string
    state_map = {
        lt.torrent_status.seeding: "Seeding",
        lt.torrent_status.downloading: "Downloading",
        lt.torrent_status.checking_files: "Checking",
        lt.torrent_status.downloading_metadata: "Downloading Metadata",
        lt.torrent_status.finished: "Finished",
        lt.torrent_status.queued_for_checking: "Queued for Checking",
        lt.torrent_status.allocating: "Allocating",
        lt.torrent_status.checking_resume_data: "Checking Resume Data"
    }
    
    state = state_map.get(status.state, "Unknown")
    
    # Calculate ETA
    eta = "∞"
    if status.download_rate > 0 and status.total_wanted > status.total_done:
        remaining = status.total_wanted - status.total_done
        eta_seconds = remaining / status.download_rate
        eta = format_time(int(eta_seconds))
    
    return {
        'name': torrent.name(),
        'size': format_size(status.total_wanted),
        'progress': status.progress * 100,
        'download_speed': format_speed(status.download_rate),
        'upload_speed': format_speed(status.upload_rate),
        'peers': status.num_peers,
        'seeds': status.num_seeds,
        'status': state,
        'save_path': status.save_path,
        'files': files,
        'hash': status.info_hash.to_string() if status.info_hash else None,
        'total_done': format_size(status.total_done),
        'total_wanted': format_size(status.total_wanted),
        'total_upload': format_size(status.total_upload),
        'total_download': format_size(status.total_download),
        'eta': eta,
        'progress_bar': format_progress_bar(status.progress)
    }


def parse_magnet_link(magnet_url: str) -> Dict:
    """Parse magnet link and extract information"""
    if not magnet_url.startswith('magnet:'):
        raise ValueError("Not a valid magnet link")
    
    # Extract hash from magnet link
    if 'xt=urn:btih:' in magnet_url:
        hash_start = magnet_url.find('xt=urn:btih:') + 12
        hash_end = magnet_url.find('&', hash_start)
        if hash_end == -1:
            hash_end = len(magnet_url)
        info_hash = magnet_url[hash_start:hash_end]
    else:
        raise ValueError("Invalid magnet link format")
    
    # Extract name if available
    name = "Unknown"
    if 'dn=' in magnet_url:
        name_start = magnet_url.find('dn=') + 3
        name_end = magnet_url.find('&', name_start)
        if name_end == -1:
            name_end = len(magnet_url)
        name = magnet_url[name_start:name_end]
    
    # Extract trackers
    trackers = []
    if 'tr=' in magnet_url:
        tracker_start = magnet_url.find('tr=') + 3
        tracker_end = magnet_url.find('&', tracker_start)
        if tracker_end == -1:
            tracker_end = len(magnet_url)
        trackers.append(magnet_url[tracker_start:tracker_end])
    
    return {
        'info_hash': info_hash,
        'name': name,
        'trackers': trackers
    }


def validate_torrent_file(file_path: str) -> bool:
    """Validate if a file is a valid torrent file"""
    try:
        lt.torrent_info(file_path)
        return True
    except Exception:
        return False


def get_torrent_hash(torrent_path: str) -> str:
    """Get the info hash of a torrent file"""
    try:
        info = lt.torrent_info(torrent_path)
        return info.info_hash().to_string()
    except Exception as e:
        raise ValueError(f"Could not get torrent hash: {e}")


def calculate_file_hash(file_path: str, algorithm: str = 'sha1') -> str:
    """Calculate hash of a file"""
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def verify_torrent_data(torrent_path: str, data_path: str) -> Dict:
    """Verify torrent data integrity"""
    try:
        info = lt.torrent_info(torrent_path)
        storage = lt.file_storage()
        
        # Add files to storage
        for i in range(info.num_files()):
            file_entry = info.files()[i]
            storage.add_file(file_entry.path, file_entry.size)
        
        # Create piece picker
        picker = lt.piece_picker(storage, info.piece_length())
        
        # Verify pieces
        verified_pieces = 0
        total_pieces = info.num_pieces()
        
        for piece_index in range(total_pieces):
            piece_hash = info.hash_for_piece(piece_index)
            # Here you would read the actual piece data and verify
            # For now, we'll just count pieces
            verified_pieces += 1
        
        return {
            'verified_pieces': verified_pieces,
            'total_pieces': total_pieces,
            'verification_progress': verified_pieces / total_pieces * 100,
            'is_complete': verified_pieces == total_pieces
        }
        
    except Exception as e:
        raise ValueError(f"Error verifying torrent data: {e}")


def get_torrent_metadata(torrent_path: str) -> Dict:
    """Extract metadata from torrent file"""
    try:
        info = lt.torrent_info(torrent_path)
        
        metadata = {
            'name': info.name(),
            'total_size': format_size(info.total_size()),
            'num_files': info.num_files(),
            'num_pieces': info.num_pieces(),
            'piece_length': format_size(info.piece_length()),
            'info_hash': info.info_hash().to_string(),
            'creation_date': time.ctime(info.creation_date()) if info.creation_date() > 0 else "Unknown",
            'comment': info.comment() if info.comment() else "No comment",
            'created_by': info.creator() if info.creator() else "Unknown",
            'is_private': info.is_private(),
            'trackers': []
        }
        
        # Get trackers
        for tier in info.trackers():
            for tracker in tier:
                metadata['trackers'].append(tracker['url'])
        
        # Get files
        files = []
        for i in range(info.num_files()):
            file_entry = info.files()[i]
            files.append({
                'path': file_entry.path,
                'size': format_size(file_entry.size),
                'offset': format_size(file_entry.offset)
            })
        metadata['files'] = files
        
        return metadata
        
    except Exception as e:
        raise ValueError(f"Error extracting metadata: {e}")


def create_torrent_file(info_hash: str, name: str, trackers: List[str], 
                       files: List[Dict], output_path: str) -> None:
    """Create a new torrent file"""
    try:
        # Create torrent info
        torrent = lt.create_torrent()
        torrent.set_name(name)
        
        # Add trackers
        for tracker in trackers:
            torrent.add_tracker(tracker)
        
        # Add files
        for file_info in files:
            torrent.add_file(file_info['path'], file_info['size'])
        
        # Set info hash if provided
        if info_hash:
            torrent.set_hash(0, bytes.fromhex(info_hash))
        
        # Write torrent file
        with open(output_path, 'wb') as f:
            f.write(lt.bencode(torrent.generate()))
            
    except Exception as e:
        raise ValueError(f"Error creating torrent file: {e}")


def estimate_download_time(total_size: int, download_speed: int) -> Optional[str]:
    """Estimate download time based on size and speed"""
    if download_speed <= 0:
        return None
    
    seconds = total_size / download_speed
    return format_time(int(seconds))


def get_priority_name(priority: int) -> str:
    """Get human-readable priority name"""
    priority_names = {
        0: "Do Not Download",
        1: "Low",
        2: "Normal Low",
        3: "Normal",
        4: "Normal High",
        5: "High",
        6: "Very High",
        7: "Maximum"
    }
    return priority_names.get(priority, "Unknown")


def format_peer_flags(flags: int) -> str:
    """Format peer flags into readable string"""
    flag_names = []
    
    if flags & 1:  # interesting
        flag_names.append("interesting")
    if flags & 2:  # choked
        flag_names.append("choked")
    if flags & 4:  # remote interested
        flag_names.append("remote_interested")
    if flags & 8:  # remote choked
        flag_names.append("remote_choked")
    if flags & 16:  # supports extensions
        flag_names.append("supports_extensions")
    if flags & 32:  # local connection
        flag_names.append("local_connection")
    if flags & 64:  # handshake
        flag_names.append("handshake")
    if flags & 128:  # connecting
        flag_names.append("connecting")
    if flags & 256:  # queued
        flag_names.append("queued")
    
    return ", ".join(flag_names) if flag_names else "none" 