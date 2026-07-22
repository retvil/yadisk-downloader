#!/usr/bin/env python3
"""Entry point for bundled executable."""

import os
import sys


def main():
    # When running as bundled exe, add _internal to path
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        internal_dir = os.path.join(exe_dir, "_internal")
        if os.path.exists(internal_dir) and internal_dir not in sys.path:
            sys.path.insert(0, internal_dir)
        if exe_dir not in sys.path:
            sys.path.insert(0, exe_dir)

    from yadisk_downloader.cli import main as cli_main
    cli_main()


if __name__ == "__main__":
    main()
