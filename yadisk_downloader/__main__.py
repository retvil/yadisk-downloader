"""Entry point for python -m yadisk_downloader."""

import os
import sys


def check_chromium():
    """Check if Chromium is installed, offer to install if not."""
    try:
        from .setup_wizard import is_chromium_installed, run_setup_if_needed
        if not is_chromium_installed():
            print("=" * 60)
            print("yadisk-downloader - First Run Setup")
            print("=" * 60)
            print()
            print("Chromium browser is required for downloading files.")
            print("It will be downloaded automatically (~200MB).")
            print()
            try:
                response = input("Install Chromium now? (y/n): ").strip().lower()
            except EOFError:
                return
            if response == "y":
                success = run_setup_if_needed()
                if not success:
                    print("Warning: Chromium installation failed.")
                    print("Some features may not work correctly.")
            else:
                print("Skipping Chromium installation.")
                print("You can install it later with: playwright install chromium")
            print()
    except (ImportError, Exception):
        pass


def main():
    """Main entry point."""
    # Add the package directory to path for bundled exe
    if getattr(sys, 'frozen', False):
        package_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        if package_dir not in sys.path:
            sys.path.insert(0, package_dir)

    # Only check Chromium for GUI mode (no arguments)
    if len(sys.argv) == 1:
        check_chromium()

    from .cli import main as cli_main
    cli_main()


if __name__ == "__main__":
    main()
