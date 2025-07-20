#!/usr/bin/env python3
"""
Test script to verify TorrentTamer installation
"""

import sys
import importlib

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✓ {package_name or module_name} imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import {package_name or module_name}: {e}")
        return False

def main():
    print("=== TorrentTamer Installation Test ===")
    print()
    
    # Test Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✓ Python {python_version.major}.{python_version.minor}.{python_version.micro} is compatible")
    else:
        print(f"✗ Python {python_version.major}.{python_version.minor}.{python_version.micro} is too old. Need 3.8+")
        return False
    
    print()
    
    # Test required modules
    required_modules = [
        ('libtorrent', 'libtorrent'),
        ('configparser', 'configparser'),
        ('argparse', 'argparse'),
        ('pathlib', 'pathlib'),
        ('typing', 'typing'),
    ]
    
    all_good = True
    for module_name, display_name in required_modules:
        if not test_import(module_name, display_name):
            all_good = False
    
    print()
    
    # Test TorrentTamer modules
    print("Testing TorrentTamer modules:")
    torrenttamer_modules = [
        'torrent_manager',
        'torrent_monitor', 
        'utils'
    ]
    
    for module_name in torrenttamer_modules:
        if not test_import(module_name):
            all_good = False
    
    print()
    
    if all_good:
        print("=== All tests passed! ===")
        print("TorrentTamer is ready to use.")
        print()
        print("Try running:")
        print("  python torrenttamer.py --help")
        return True
    else:
        print("=== Some tests failed! ===")
        print("Please check the installation and try again.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 