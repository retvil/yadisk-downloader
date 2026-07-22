"""System notifications for yadisk-downloader."""

import os
import platform
import subprocess


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
            # Use PowerShell toast notification
            ps_cmd = f"""
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null

            $template = @"
            <toast>
                <visual>
                    <binding template="ToastGeneric">
                        <text>{title}</text>
                        <text>{message}</text>
                    </binding>
                </visual>
            </toast>
"@

            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("yadisk-downloader").Show($toast)
            """
            subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                timeout=10,
            )
            return True

        elif system == "Darwin":
            # macOS: use osascript
            subprocess.run(
                [
                    "osascript", "-e",
                    f'display notification "{message}" with title "{title}"',
                ],
                capture_output=True,
                timeout=10,
            )
            return True

        else:
            # Linux: use notify-send
            subprocess.run(
                ["notify-send", title, message],
                capture_output=True,
                timeout=10,
            )
            return True

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
