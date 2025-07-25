#!/usr/bin/env python3
"""
Setup script for TorrentTamer
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="torrenttamer",
    version="1.0.0",
    author="makalin",
    description="A lightweight, terminal-based torrent manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/makalin/torrenttamer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: File Transfer Protocol (FTP)",
        "Topic :: System :: Networking",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "torrenttamer=torrenttamer:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 