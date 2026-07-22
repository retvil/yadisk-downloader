#!/usr/bin/env python3
"""Entry point for bundled executable."""

import os
import sys

# Add the package directory to path
if getattr(sys, 'frozen', False):
    package_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    if package_dir not in sys.path:
        sys.path.insert(0, package_dir)

# Import and run
from yadisk_downloader.cli import main

if __name__ == "__main__":
    main()
