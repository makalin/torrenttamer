#!/usr/bin/env python3
"""
Advanced Example - Demonstrating all TorrentTamer features
"""

import time
from torrenttamer import TorrentTamer
from advanced_features import (
    TorrentScheduler, RSSFeedManager, TorrentAutomation, 
    TorrentStatistics, TorrentBackup
)


def main():
    print("=== TorrentTamer Advanced Features Demo ===")
    print()
    
    # Initialize TorrentTamer
    print("Initializing TorrentTamer...")
    app = TorrentTamer()
    print("✓ TorrentTamer initialized successfully")
    print()
    
    # Initialize advanced features
    print("Initializing advanced features...")
    scheduler = TorrentScheduler(app.torrent_manager)
    rss_manager = RSSFeedManager(app.torrent_manager, "~/Downloads")
    automation = TorrentAutomation(app.torrent_manager)
    statistics = TorrentStatistics(app.torrent_manager)
    backup = TorrentBackup(app.torrent_manager)
    print("✓ Advanced features initialized")
    print()
    
    # Demonstrate Priority Management
    print("=== Priority Management ===")
    print("Priority levels: 0=Do Not Download, 1=Low, 2=Normal Low, 3=Normal,")
    print("4=Normal High, 5=High, 6=Very High, 7=Maximum")
    print()
    print("Commands:")
    print("  app.set_priority(torrent_id, priority)")
    print("  app.set_file_priority(torrent_id, file_index, priority)")
    print()
    
    # Demonstrate Tracker Management
    print("=== Tracker Management ===")
    print("Commands:")
    print("  app.add_trackers(torrent_id, ['http://tracker1.com', 'http://tracker2.com'])")
    print("  app.remove_trackers(torrent_id, ['http://bad-tracker.com'])")
    print()
    
    # Demonstrate Advanced Download Features
    print("=== Advanced Download Features ===")
    print("Commands:")
    print("  app.set_sequential_download(torrent_id, True)  # For streaming")
    print("  app.set_super_seeding(torrent_id, True)        # For initial seeding")
    print("  app.force_recheck(torrent_id)                  # Verify data integrity")
    print()
    
    # Demonstrate Scheduling
    print("=== Scheduling ===")
    print("Example: Schedule torrent to start at 9 AM on weekdays")
    print("  scheduler.add_schedule('morning_start', 1, 'start', '09:00',")
    print("                        ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'])")
    print()
    print("Example: Schedule torrent to stop at 11 PM daily")
    print("  scheduler.add_schedule('night_stop', 1, 'stop', '23:00')")
    print()
    print("  scheduler.start_scheduler()  # Start the scheduler")
    print()
    
    # Demonstrate RSS Feeds
    print("=== RSS Feed Management ===")
    print("Example: Add RSS feed for automatic downloads")
    print("  rss_manager.add_feed('linux_iso', 'https://example.com/linux.rss')")
    print("  rss_manager.add_filter('linux_iso', 'Ubuntu', priority=7)")
    print("  rss_manager.add_filter('linux_iso', 'Debian', priority=6)")
    print("  rss_manager.start_rss_monitor()  # Start RSS monitoring")
    print()
    
    # Demonstrate Automation
    print("=== Automation Rules ===")
    print("Example: Auto-pause when disk space is low")
    print("  def low_disk_space():")
    print("      return get_free_space() < 10 * 1024 * 1024 * 1024  # 10GB")
    print("  ")
    print("  def pause_all_torrents():")
    print("      for torrent_id in app.torrent_manager.get_torrents():")
    print("          app.torrent_manager.pause_torrent(torrent_id)")
    print("  ")
    print("  automation.add_rule('low_disk', low_disk_space, pause_all_torrents)")
    print()
    
    # Demonstrate Statistics
    print("=== Statistics and Analytics ===")
    print("Commands:")
    print("  statistics.update_stats()           # Update current statistics")
    print("  daily_stats = statistics.get_daily_stats()")
    print("  weekly_stats = statistics.get_weekly_stats()")
    print()
    
    # Demonstrate Backup and Restore
    print("=== Backup and Restore ===")
    print("Commands:")
    print("  backup_file = backup.create_backup('my_backup')")
    print("  backup.restore_backup(backup_file)")
    print("  available_backups = backup.list_backups()")
    print()
    
    # Demonstrate Enhanced Monitoring
    print("=== Enhanced Monitoring ===")
    print("The monitor now supports:")
    print("  - Priority display")
    print("  - Piece availability visualization")
    print("  - Peer information")
    print("  - Interactive controls (press 'p' for pieces, 'e' for peers)")
    print()
    
    # Demonstrate Search and Filtering
    print("=== Search and Filtering ===")
    print("Commands:")
    print("  app.list_torrents()                    # List all torrents")
    print("  app.list_torrents('downloading')       # Filter by status")
    print("  app.search_torrents('ubuntu')          # Search by name")
    print()
    
    # Demonstrate Export and Import
    print("=== Export and Import ===")
    print("Commands:")
    print("  app.export_torrent(torrent_id, 'exported.torrent')")
    print("  app.add_torrent('exported.torrent')")
    print()
    
    # Show current configuration
    print("=== Current Configuration ===")
    for section in app.config.sections():
        print(f"[{section}]")
        for key, value in app.config[section].items():
            print(f"  {key} = {value}")
    print()
    
    # Show session statistics
    print("=== Session Statistics ===")
    app.get_session_stats()
    print()
    
    print("=== Demo Completed ===")
    print("All advanced features are now available in TorrentTamer!")
    print("For more information, see the README.md file")


if __name__ == "__main__":
    main() 