"""Entry point for python -m yadisk_downloader."""

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
            response = input("Install Chromium now? (y/n): ").strip().lower()
            if response == "y":
                success = run_setup_if_needed()
                if not success:
                    print("Warning: Chromium installation failed.")
                    print("Some features may not work correctly.")
            else:
                print("Skipping Chromium installation.")
                print("You can install it later with: playwright install chromium")
            print()
    except ImportError:
        pass


def main():
    """Main entry point."""
    # Check for GUI mode
    if len(sys.argv) == 1 or "--gui" in sys.argv:
        check_chromium()

    from .cli import main as cli_main
    cli_main()


if __name__ == "__main__":
    main()
