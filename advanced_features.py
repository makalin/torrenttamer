#!/usr/bin/env python3
"""
Advanced Features - Extended functionality for TorrentTamer
"""

import json
import os
import schedule
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable
import xml.etree.ElementTree as ET
import requests

import libtorrent as lt

from torrent_manager import TorrentManager
from utils import format_size, get_torrent_metadata


class TorrentScheduler:
    """Schedule torrent operations"""
    
    def __init__(self, torrent_manager: TorrentManager):
        self.torrent_manager = torrent_manager
        self.schedules = {}
        self.running = False
        self.thread = None
    
    def add_schedule(self, schedule_id: str, torrent_id: int, 
                    operation: str, time_str: str, days: List[str] = None) -> None:
        """Add a scheduled operation"""
        if operation not in ['start', 'stop', 'pause', 'resume']:
            raise ValueError("Invalid operation")
        
        self.schedules[schedule_id] = {
            'torrent_id': torrent_id,
            'operation': operation,
            'time': time_str,
            'days': days or ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        }
    
    def remove_schedule(self, schedule_id: str) -> None:
        """Remove a scheduled operation"""
        if schedule_id in self.schedules:
            del self.schedules[schedule_id]
    
    def start_scheduler(self) -> None:
        """Start the scheduler"""
        self.running = True
        self.thread = threading.Thread(target=self._scheduler_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop_scheduler(self) -> None:
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop"""
        while self.running:
            current_time = datetime.now()
            current_day = current_time.strftime('%A').lower()
            current_time_str = current_time.strftime('%H:%M')
            
            for schedule_id, schedule_info in self.schedules.items():
                if (current_day in schedule_info['days'] and 
                    current_time_str == schedule_info['time']):
                    self._execute_schedule(schedule_id, schedule_info)
            
            time.sleep(60)  # Check every minute
    
    def _execute_schedule(self, schedule_id: str, schedule_info: Dict) -> None:
        """Execute a scheduled operation"""
        try:
            torrent_id = schedule_info['torrent_id']
            operation = schedule_info['operation']
            
            if operation == 'start':
                self.torrent_manager.resume_torrent(torrent_id)
            elif operation == 'stop':
                self.torrent_manager.pause_torrent(torrent_id)
            elif operation == 'pause':
                self.torrent_manager.pause_torrent(torrent_id)
            elif operation == 'resume':
                self.torrent_manager.resume_torrent(torrent_id)
            
            print(f"✓ Executed scheduled {operation} for torrent {torrent_id}")
            
        except Exception as e:
            print(f"✗ Error executing schedule {schedule_id}: {e}")


class RSSFeedManager:
    """Manage RSS feeds for automatic torrent downloads"""
    
    def __init__(self, torrent_manager: TorrentManager, download_path: str):
        self.torrent_manager = torrent_manager
        self.download_path = download_path
        self.feeds = {}
        self.filters = {}
        self.running = False
        self.thread = None
    
    def add_feed(self, feed_id: str, feed_url: str, check_interval: int = 3600) -> None:
        """Add an RSS feed"""
        self.feeds[feed_id] = {
            'url': feed_url,
            'check_interval': check_interval,
            'last_check': None,
            'downloaded_items': set()
        }
    
    def remove_feed(self, feed_id: str) -> None:
        """Remove an RSS feed"""
        if feed_id in self.feeds:
            del self.feeds[feed_id]
    
    def add_filter(self, feed_id: str, filter_pattern: str, priority: int = 5) -> None:
        """Add a filter for an RSS feed"""
        if feed_id not in self.filters:
            self.filters[feed_id] = []
        
        self.filters[feed_id].append({
            'pattern': filter_pattern,
            'priority': priority
        })
    
    def start_rss_monitor(self) -> None:
        """Start RSS monitoring"""
        self.running = True
        self.thread = threading.Thread(target=self._rss_monitor_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def stop_rss_monitor(self) -> None:
        """Stop RSS monitoring"""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _rss_monitor_loop(self) -> None:
        """Main RSS monitoring loop"""
        while self.running:
            for feed_id, feed_info in self.feeds.items():
                try:
                    self._check_feed(feed_id, feed_info)
                except Exception as e:
                    print(f"✗ Error checking RSS feed {feed_id}: {e}")
            
            time.sleep(300)  # Check every 5 minutes
    
    def _check_feed(self, feed_id: str, feed_info: Dict) -> None:
        """Check a single RSS feed"""
        try:
            response = requests.get(feed_info['url'], timeout=30)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            
            for item in root.findall('.//item'):
                title = item.find('title')
                link = item.find('link')
                
                if title is not None and link is not None:
                    title_text = title.text
                    link_text = link.text
                    
                    # Check if already downloaded
                    if link_text in feed_info['downloaded_items']:
                        continue
                    
                    # Check filters
                    if self._matches_filters(feed_id, title_text):
                        # Download torrent
                        try:
                            torrent_id = self.torrent_manager.add_torrent(link_text)
                            feed_info['downloaded_items'].add(link_text)
                            print(f"✓ Auto-downloaded from RSS: {title_text}")
                        except Exception as e:
                            print(f"✗ Error downloading from RSS: {e}")
            
            feed_info['last_check'] = datetime.now()
            
        except Exception as e:
            print(f"✗ Error parsing RSS feed {feed_id}: {e}")
    
    def _matches_filters(self, feed_id: str, title: str) -> bool:
        """Check if title matches any filters"""
        if feed_id not in self.filters:
            return True  # No filters, download everything
        
        title_lower = title.lower()
        for filter_info in self.filters[feed_id]:
            if filter_info['pattern'].lower() in title_lower:
                return True
        
        return False


class TorrentAutomation:
    """Automation features for torrent management"""
    
    def __init__(self, torrent_manager: TorrentManager):
        self.torrent_manager = torrent_manager
        self.rules = {}
    
    def add_rule(self, rule_id: str, condition: Callable, action: Callable) -> None:
        """Add an automation rule"""
        self.rules[rule_id] = {
            'condition': condition,
            'action': action,
            'enabled': True
        }
    
    def remove_rule(self, rule_id: str) -> None:
        """Remove an automation rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
    
    def enable_rule(self, rule_id: str) -> None:
        """Enable an automation rule"""
        if rule_id in self.rules:
            self.rules[rule_id]['enabled'] = True
    
    def disable_rule(self, rule_id: str) -> None:
        """Disable an automation rule"""
        if rule_id in self.rules:
            self.rules[rule_id]['enabled'] = False
    
    def check_rules(self) -> None:
        """Check and execute automation rules"""
        for rule_id, rule_info in self.rules.items():
            if not rule_info['enabled']:
                continue
            
            try:
                if rule_info['condition']():
                    rule_info['action']()
            except Exception as e:
                print(f"✗ Error executing rule {rule_id}: {e}")


class TorrentStatistics:
    """Advanced statistics and analytics"""
    
    def __init__(self, torrent_manager: TorrentManager):
        self.torrent_manager = torrent_manager
        self.stats_file = Path("torrent_stats.json")
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict:
        """Load statistics from file"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'total_downloaded': 0,
            'total_uploaded': 0,
            'torrents_completed': 0,
            'session_start': datetime.now().isoformat(),
            'torrent_history': []
        }
    
    def _save_stats(self) -> None:
        """Save statistics to file"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"✗ Error saving statistics: {e}")
    
    def update_stats(self) -> None:
        """Update current statistics"""
        session_stats = self.torrent_manager.get_session_stats()
        
        self.stats['total_downloaded'] = session_stats['total_download']
        self.stats['total_uploaded'] = session_stats['total_upload']
        
        # Check for completed torrents
        torrents = self.torrent_manager.get_torrents()
        for torrent_id, torrent in torrents.items():
            status = torrent.status()
            if status.progress >= 1.0 and torrent_id not in [h['id'] for h in self.stats['torrent_history']]:
                self.stats['torrents_completed'] += 1
                self.stats['torrent_history'].append({
                    'id': torrent_id,
                    'name': torrent.name(),
                    'size': status.total_wanted,
                    'completed_at': datetime.now().isoformat()
                })
        
        self._save_stats()
    
    def get_daily_stats(self) -> Dict:
        """Get daily statistics"""
        today = datetime.now().date()
        daily_downloaded = 0
        daily_uploaded = 0
        
        # Calculate daily stats from history
        for entry in self.stats['torrent_history']:
            entry_date = datetime.fromisoformat(entry['completed_at']).date()
            if entry_date == today:
                daily_downloaded += entry['size']
        
        return {
            'date': today.isoformat(),
            'downloaded': format_size(daily_downloaded),
            'uploaded': format_size(daily_uploaded),
            'torrents_completed': len([e for e in self.stats['torrent_history'] 
                                     if datetime.fromisoformat(e['completed_at']).date() == today])
        }
    
    def get_weekly_stats(self) -> Dict:
        """Get weekly statistics"""
        week_ago = datetime.now() - timedelta(days=7)
        weekly_downloaded = 0
        weekly_uploaded = 0
        
        for entry in self.stats['torrent_history']:
            entry_date = datetime.fromisoformat(entry['completed_at'])
            if entry_date >= week_ago:
                weekly_downloaded += entry['size']
        
        return {
            'period': '7 days',
            'downloaded': format_size(weekly_downloaded),
            'uploaded': format_size(weekly_uploaded),
            'torrents_completed': len([e for e in self.stats['torrent_history'] 
                                     if datetime.fromisoformat(e['completed_at']) >= week_ago])
        }


class TorrentBackup:
    """Backup and restore torrent sessions"""
    
    def __init__(self, torrent_manager: TorrentManager):
        self.torrent_manager = torrent_manager
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, backup_name: str = None) -> str:
        """Create a backup of current session"""
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'torrents': []
        }
        
        torrents = self.torrent_manager.get_torrents()
        for torrent_id, torrent in torrents.items():
            status = torrent.status()
            info = torrent.get_torrent_info()
            
            torrent_data = {
                'id': torrent_id,
                'name': torrent.name(),
                'save_path': status.save_path,
                'priority': torrent.get_priority(),
                'info_hash': status.info_hash.to_string() if status.info_hash else None
            }
            
            if info:
                torrent_data['files'] = []
                for i in range(info.num_files()):
                    file_entry = info.files()[i]
                    torrent_data['files'].append({
                        'path': file_entry.path,
                        'size': file_entry.size,
                        'priority': file_entry.priority
                    })
            
            backup_data['torrents'].append(torrent_data)
        
        backup_file = self.backup_dir / f"{backup_name}.json"
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        return str(backup_file)
    
    def restore_backup(self, backup_file: str) -> None:
        """Restore from backup"""
        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            # Clear current torrents
            current_torrents = list(self.torrent_manager.get_torrents().keys())
            for torrent_id in current_torrents:
                self.torrent_manager.remove_torrent(torrent_id)
            
            # Restore torrents from backup
            for torrent_data in backup_data['torrents']:
                # Note: This would need magnet links or torrent files to fully restore
                # For now, we'll just log what would be restored
                print(f"Would restore: {torrent_data['name']} (ID: {torrent_data['id']})")
            
        except Exception as e:
            print(f"✗ Error restoring backup: {e}")
    
    def list_backups(self) -> List[str]:
        """List available backups"""
        backups = []
        for backup_file in self.backup_dir.glob("*.json"):
            backups.append(backup_file.name)
        return sorted(backups) 