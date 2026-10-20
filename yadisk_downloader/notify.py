"""System notifications for yadisk-downloader."""

import platform
import subprocess
from xml.sax.saxutils import escape as xml_escape


def _ps_escape(text: str) -> str:
    """Escape text for interpolation inside a PowerShell expandable here-string."""
    return text.replace("`", "``").replace("$", "`$")


def _applescript_escape(text: str) -> str:
    """Escape text for an AppleScript double-quoted string literal."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def send_notification(title: str, message: str) -> bool:
    """Send a system notification.

    Args:
        title: Notification title.
        message: Notification message.

    Returns:
        True if notification was sent successfully.
    """
    system = platform.system()

    try:
        if system == "Windows":
            # XML-escape first (LoadXml), then PowerShell-escape ($ and ` would
            # be interpolated inside the expandable here-string)
            safe_title = _ps_escape(xml_escape(title))
            safe_message = _ps_escape(xml_escape(message))
            ps_cmd = f"""
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null

            $template = @"
            <toast>
                <visual>
                    <binding template="ToastGeneric">
                        <text>{safe_title}</text>
                        <text>{safe_message}</text>
                    </binding>
                </visual>
            </toast>
"@

            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("yadisk-downloader").Show($toast)
            """
            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0

        elif system == "Darwin":
            # macOS: use osascript
            result = subprocess.run(
                [
                    "osascript", "-e",
                    f'display notification "{_applescript_escape(message)}" '
                    f'with title "{_applescript_escape(title)}"',
                ],
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0

        else:
            # Linux: use notify-send (arguments passed directly, no shell)
            result = subprocess.run(
                ["notify-send", title, message],
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0

    except Exception:
        return False


def notify_download_complete(total_files: int, success: int, failed: int):
    """Send notification about download completion."""
    if failed > 0:
        title = "yadisk-downloader: Download complete with errors"
        message = f"{success}/{total_files} files downloaded, {failed} failed"
    else:
        title = "yadisk-downloader: Download complete"
        message = f"All {total_files} files downloaded successfully"

    send_notification(title, message)
