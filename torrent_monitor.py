#!/usr/bin/env python3
"""
Torrent Monitor - Real-time monitoring functionality
"""

import os
import sys
import time
from typing import Dict

import libtorrent as lt

from utils import format_size, format_speed


class TorrentMonitor:
    def __init__(self, torrent_manager):
        self.torrent_manager = torrent_manager
        self.running = False
        self.show_pieces = False
        self.show_peers = False

    def start(self, show_pieces: bool = False, show_peers: bool = False) -> None:
        """Start real-time monitoring"""
        self.running = True
        self.show_pieces = show_pieces
        self.show_peers = show_peers
        
        print("Starting real-time monitoring... (Press Ctrl+C to stop)")
        print("Press 'p' to toggle piece view, 'e' to toggle peer view")
        print()
        
        try:
            while self.running:
                self._clear_screen()
                self._display_header()
                self._display_torrents()
                self._display_session_stats()
                
                # Check for user input (non-blocking)
                if self._check_user_input():
                    continue
                
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False

    def _clear_screen(self) -> None:
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def _display_header(self) -> None:
        """Display monitoring header"""
        print("=" * 100)
        print("TORRENT TAMER - REAL-TIME MONITOR")
        print("=" * 100)
        print()

    def _display_torrents(self) -> None:
        """Display all active torrents"""
        torrents = self.torrent_manager.get_torrents()
        
        if not torrents:
            print("No active torrents found.")
            print()
            return
        
        print(f"{'ID':<4} {'Name':<35} {'Progress':<10} {'DL Speed':<12} {'UL Speed':<12} {'Peers':<6} {'Status':<12} {'Priority':<8}")
        print("-" * 105)
        
        for torrent_id, torrent in torrents.items():
            status = torrent.status()
            name = torrent.name()[:34] + "..." if len(torrent.name()) > 35 else torrent.name()
            progress = f"{status.progress * 100:.1f}%"
            dl_speed = format_speed(status.download_rate)
            ul_speed = format_speed(status.upload_rate)
            peers = f"{status.num_peers}"
            state = str(status.state).split('.')[-1].replace('_', ' ').title()
            priority = torrent.get_priority()
            
            print(f"{torrent_id:<4} {name:<35} {progress:<10} {dl_speed:<12} {ul_speed:<12} {peers:<6} {state:<12} {priority:<8}")
        
        print()
        
        # Show piece availability if enabled
        if self.show_pieces and torrents:
            self._display_piece_availability(list(torrents.values())[0])
        
        # Show peer information if enabled
        if self.show_peers and torrents:
            self._display_peer_information(list(torrents.keys())[0])

    def _display_piece_availability(self, torrent: lt.torrent_handle) -> None:
        """Display piece availability for a torrent"""
        try:
            pieces = torrent.get_piece_availability()
            if not pieces:
                return
            
            print("PIECE AVAILABILITY:")
            print("-" * 50)
            
            # Show piece map
            piece_map = ""
            for i, availability in enumerate(pieces):
                if availability > 0:
                    piece_map += "█"  # Available
                else:
                    piece_map += "░"  # Not available
                
                if (i + 1) % 50 == 0:
                    piece_map += "\n"
            
            print(piece_map)
            print()
            
        except Exception as e:
            print(f"Error displaying pieces: {e}")

    def _display_peer_information(self, torrent_id: int) -> None:
        """Display peer information for a torrent"""
        try:
            peers = self.torrent_manager.get_torrent_peers(torrent_id)
            if not peers:
                return
            
            print("PEER INFORMATION:")
            print("-" * 50)
            print(f"{'IP':<15} {'Port':<6} {'Client':<20} {'Progress':<10} {'DL':<8} {'UL':<8}")
            print("-" * 50)
            
            for peer in peers[:10]:  # Show first 10 peers
                ip = str(peer['ip'])
                port = str(peer['port'])
                client = peer['client'][:19] + "..." if len(peer['client']) > 20 else peer['client']
                progress = f"{peer['progress'] * 100:.1f}%"
                dl_speed = format_speed(peer['download_rate'])
                ul_speed = format_speed(peer['upload_rate'])
                
                print(f"{ip:<15} {port:<6} {client:<20} {progress:<10} {dl_speed:<8} {ul_speed:<8}")
            
            if len(peers) > 10:
                print(f"... and {len(peers) - 10} more peers")
            print()
            
        except Exception as e:
            print(f"Error displaying peers: {e}")

    def _display_session_stats(self) -> None:
        """Display session statistics"""
        stats = self.torrent_manager.get_session_stats()
        
        print("SESSION STATISTICS:")
        print("-" * 40)
        print(f"Total Download: {format_size(stats['total_download'])}")
        print(f"Total Upload:   {format_size(stats['total_upload'])}")
        print(f"Download Rate:  {format_speed(stats['download_rate'])}")
        print(f"Upload Rate:    {format_speed(stats['upload_rate'])}")
        print(f"Active Peers:   {stats['num_peers']}")
        print(f"Active Torrents: {stats['num_torrents']}")
        print()
        print("Controls: 'p' - Toggle pieces, 'e' - Toggle peers, Ctrl+C - Stop")
        print()

    def _check_user_input(self) -> bool:
        """Check for user input (non-blocking)"""
        try:
            import msvcrt  # Windows
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8').lower()
                if key == 'p':
                    self.show_pieces = not self.show_pieces
                    return True
                elif key == 'e':
                    self.show_peers = not self.show_peers
                    return True
        except ImportError:
            try:
                import tty
                import termios
                import select
                
                # Check if input is available
                if select.select([sys.stdin], [], [], 0)[0]:
                    key = sys.stdin.read(1).lower()
                    if key == 'p':
                        self.show_pieces = not self.show_pieces
                        return True
                    elif key == 'e':
                        self.show_peers = not self.show_peers
                        return True
            except:
                pass
        
        return False

    def stop(self) -> None:
        """Stop monitoring"""
        self.running = False 