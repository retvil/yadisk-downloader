"""GUI interface for yadisk-downloader using ttkbootstrap."""

import json
import os
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

try:
    import ttkbootstrap as ttk
except ImportError:
    ttk = None

from . import __version__
from .core.api import get_download_url, list_files
from .core.converter import PRESETS, convert, get_output_path
from .core.downloader import download_file
from .translations import LANG_DISPLAY_NAMES, detect_system_language, t
from .utils import find_ffmpeg, format_size

APP_AUTHOR = "retvil"
GITHUB_URL = "https://github.com/retvil/yadisk-downloader"
TEXT_MUTED = "#6b7280"
FILE_TYPES = ["video", "audio", "image", "document", "archive", "executable", "other"]
GUI_SETTINGS_FILE = Path.home() / ".yadisk-downloader" / "gui.json"


def _load_language() -> str:
    """Load the saved GUI language, falling back to the system language."""
    try:
        data = json.loads(GUI_SETTINGS_FILE.read_text(encoding="utf-8"))
        lang = data.get("language")
        if lang in LANG_DISPLAY_NAMES:
            return lang
    except Exception:
        pass
    return detect_system_language()


def _save_language(lang: str) -> None:
    """Persist the GUI language choice."""
    try:
        GUI_SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        GUI_SETTINGS_FILE.write_text(json.dumps({"language": lang}), encoding="utf-8")
    except Exception:
        pass


class ToolTip:
    """Minimal hover tooltip bound to a widget."""

    def __init__(self, widget, get_text):
        self.widget = widget
        self.get_text = get_text
        self.tip = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, event=None):
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self.tip, text=self.get_text(), background="#ffffe0",
            relief="solid", borderwidth=1, font=("Segoe UI", 9),
        ).pack()

    def _hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


if ttk is not None:
    class App(ttk.Window):
        def __init__(self):
            super().__init__(themename="flatly", size=(900, 750), minsize=(800, 600))

            try:
                icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
                if os.path.exists(icon_path):
                    self.iconbitmap(icon_path)
            except Exception:
                pass

            self.language = _load_language()
            self.files = []
            self.folders = []
            self.file_checkboxes = []
            self.cancel_event = threading.Event()
            self._link_placeholder_active = False

            self._build_ui()
            self.update_ui()

        def _build_ui(self):
            # Footer: packed FIRST (bottom) so it keeps its space on resize
            footer = ttk.Frame(self, padding=(16, 4, 16, 10))
            footer.pack(side="bottom", fill="x")
            self.github_link = ttk.Label(
                footer, text="GitHub", font=("Segoe UI", 9, "underline"),
                foreground="#0369a1", cursor="hand2",
            )
            self.github_link.pack(side="right")
            self.github_link.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_URL))
            self.footer_label = ttk.Label(
                footer, font=("Segoe UI", 9), foreground=TEXT_MUTED,
            )
            self.footer_label.pack(side="right", padx=(0, 4))

            # Status bar above footer
            self.status_label = ttk.Label(
                self, font=("Segoe UI", 10), anchor="w", padding=(20, 4),
            )
            self.status_label.pack(side="bottom", fill="x")

            main = ttk.Frame(self, padding=(15, 10))
            main.pack(fill="both", expand=True)

            # Language selector: top-right
            lang_bar = ttk.Frame(main)
            lang_bar.pack(fill="x")
            self.lang_menu = ttk.Combobox(
                lang_bar, values=list(LANG_DISPLAY_NAMES.values()),
                state="readonly", width=13,
            )
            self.lang_menu.set(LANG_DISPLAY_NAMES[self.language])
            self.lang_menu.bind("<<ComboboxSelected>>", self._on_language_change)
            self.lang_menu.pack(side="right")
            self.lang_label = ttk.Label(lang_bar, foreground=TEXT_MUTED)
            self.lang_label.pack(side="right", padx=(0, 8))

            # Link row
            link_frame = ttk.Frame(main)
            link_frame.pack(fill="x", pady=(8, 10))
            self.link_label = ttk.Label(link_frame)
            self.link_label.pack(side="left", padx=(0, 5))
            self.link_entry = ttk.Entry(link_frame)
            self.link_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
            self.link_entry.bind("<Control-v>", self._paste_from_clipboard)
            self.link_entry.bind("<Button-3>", self._show_context_menu)
            self.link_entry.bind("<FocusIn>", self._clear_link_placeholder)
            self.link_entry.bind("<FocusOut>", self._set_link_placeholder)
            self.scan_btn = ttk.Button(
                link_frame, width=12, bootstyle="info", command=self._scan,
            )
            self.scan_btn.pack(side="right")

            # Settings row
            settings_frame = ttk.Frame(main)
            settings_frame.pack(fill="x", pady=(0, 10))

            res_frame = ttk.Frame(settings_frame)
            res_frame.pack(side="left", padx=(0, 20))
            self.res_label = ttk.Label(res_frame)
            self.res_label.pack(side="left", padx=(0, 5))
            self.res_var = tk.StringVar(value="720p")
            for res in ["240p", "360p", "480p", "720p", "1080p"]:
                ttk.Radiobutton(
                    res_frame, text=res, variable=self.res_var, value=res,
                ).pack(side="left", padx=2)

            out_frame = ttk.Frame(settings_frame)
            out_frame.pack(side="left", fill="x", expand=True)
            self.output_label = ttk.Label(out_frame)
            self.output_label.pack(side="left", padx=(0, 5))
            self.output_entry = ttk.Entry(out_frame)
            self.output_entry.insert(0, "./downloads")
            self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
            self.output_var = tk.StringVar(value="./downloads")
            self.output_var.trace_add("write", self._update_path_preview)
            ttk.Button(out_frame, text="...", width=3, command=self._browse_output).pack(side="right")

            row2 = ttk.Frame(main)
            row2.pack(fill="x", pady=(0, 10))

            folder_frame = ttk.Frame(row2)
            folder_frame.pack(side="left", padx=(0, 15))
            self.folder_label = ttk.Label(folder_frame)
            self.folder_label.pack(side="left", padx=(0, 5))
            self.folder_var = tk.StringVar()
            self.folder_menu = ttk.Combobox(
                folder_frame, textvariable=self.folder_var,
                state="readonly", width=16,
            )
            self.folder_menu.pack(side="left")

            type_frame = ttk.Frame(row2)
            type_frame.pack(side="left", padx=(0, 15))
            self.type_label = ttk.Label(type_frame)
            self.type_label.pack(side="left", padx=(0, 5))
            self.type_var = tk.StringVar()
            self.type_menu = ttk.Combobox(
                type_frame, textvariable=self.type_var,
                state="readonly", width=12,
            )
            self.type_menu.bind("<<ComboboxSelected>>", lambda e: self._update_file_list())
            self.type_menu.pack(side="left")

            preset_frame = ttk.Frame(row2)
            preset_frame.pack(side="left", fill="x", expand=True)
            self.convert_label = ttk.Label(preset_frame)
            self.convert_label.pack(side="left", padx=(0, 5))
            self.preset_var = tk.StringVar()
            self.preset_menu = ttk.Combobox(
                preset_frame, textvariable=self.preset_var, state="readonly",
            )
            self.preset_menu.pack(side="left", fill="x", expand=True)
            self.delete_var = tk.BooleanVar(value=False)
            self.delete_check = ttk.Checkbutton(preset_frame, variable=self.delete_var)
            self.delete_check.pack(side="left", padx=(10, 0))

            btn_frame = ttk.Frame(main)
            btn_frame.pack(fill="x", pady=(0, 10))
            self.download_btn = ttk.Button(
                btn_frame, bootstyle="success", command=self._download,
            )
            self.download_btn.pack(side="left")
            # pack order: select_none first (rightmost), select_all second
            # → visual left-to-right: [Select All][Select None]
            self.select_none_btn = ttk.Button(btn_frame, width=12, command=self._select_none)
            self.select_none_btn.pack(side="right")
            self.select_all_btn = ttk.Button(btn_frame, width=12, command=self._select_all)
            self.select_all_btn.pack(side="right", padx=(5, 0))

            # File list: canvas-based scrollable frame of checkbuttons
            list_frame = ttk.Frame(main)
            list_frame.pack(fill="both", expand=True, pady=(0, 10))
            self.canvas = tk.Canvas(list_frame, highlightthickness=0)
            self.placeholder_id = self.canvas.create_text(
                0, 0, text="", font=("Segoe UI", 12), fill=TEXT_MUTED,
            )
            self.scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.canvas.yview)
            self.file_scroll = ttk.Frame(self.canvas)
            self.file_scroll.bind(
                "<Configure>",
                lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
            )
            self.canvas_window = self.canvas.create_window((0, 0), window=self.file_scroll, anchor="nw")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            self.canvas.pack(side="left", fill="both", expand=True)
            self.canvas.bind(
                "<Configure>",
                lambda e: (
                    self.canvas.itemconfigure(self.canvas_window, width=e.width),
                    self.canvas.coords(self.placeholder_id, e.width / 2, e.height / 2),
                ),
            )
            # Wheel scrolls the list only while the pointer is over it
            self.bind_all("<MouseWheel>", self._on_wheel)

            self.path_label = ttk.Label(main, anchor="w", foreground=TEXT_MUTED)
            self.path_label.pack(fill="x")
            self.progress = ttk.Progressbar(main, mode="determinate")
            self.progress.pack(fill="x", pady=(5, 0))
            self.progress.configure(value=0)

            # Tooltips
            ToolTip(self.delete_check, lambda: t(self.language, "tooltip_delete"))
            ToolTip(self.preset_menu, lambda: t(self.language, "tooltip_preset"))

            # Initial sentinel values
            self.folder_var.set(t(self.language, "all_folders"))
            self.type_var.set(t(self.language, "all_types"))
            self.preset_var.set(t(self.language, "no_conversion"))
            self._set_link_placeholder()

        def _on_wheel(self, event):
            cx = self.canvas.winfo_rootx()
            cy = self.canvas.winfo_rooty()
            if (
                cx <= event.x_root <= cx + self.canvas.winfo_width()
                and cy <= event.y_root <= cy + self.canvas.winfo_height()
            ):
                self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

        def _on_language_change(self, event=None):
            prev_lang = self.language
            prev_folder = self.folder_var.get()
            prev_type = self.type_var.get()
            prev_preset = self._get_preset_name()
            choice = self.lang_menu.get()
            for code, display in LANG_DISPLAY_NAMES.items():
                if display == choice:
                    self.language = code
                    break
            _save_language(self.language)
            self.update_ui()
            # Remap sentinel values, keep concrete selections
            if prev_folder == t(prev_lang, "all_folders") or prev_folder not in self.folders:
                self.folder_var.set(t(self.language, "all_folders"))
            if prev_type == t(prev_lang, "all_types") or prev_type not in FILE_TYPES:
                self.type_var.set(t(self.language, "all_types"))
            if prev_preset is None:
                self.preset_var.set(t(self.language, "no_conversion"))
            else:
                for v in self.preset_menu.cget("values"):
                    if str(v).split(" — ")[0] == prev_preset:
                        self.preset_var.set(v)
                        break

        def update_ui(self):
            """Refresh every translatable text in the interface."""
            lang = self.language
            self.title(t(lang, "title"))
            self.lang_label.configure(text=t(lang, "lang_label"))
            self.link_label.configure(text=t(lang, "link_label"))
            self.scan_btn.configure(text=t(lang, "scan_btn"))
            self.res_label.configure(text=t(lang, "resolution_label"))
            self.output_label.configure(text=t(lang, "output_label"))
            self.folder_label.configure(text=t(lang, "folder_label"))
            self.type_label.configure(text=t(lang, "type_label"))
            self.convert_label.configure(text=t(lang, "convert_label"))
            self.delete_check.configure(text=t(lang, "delete_original"))
            self.download_btn.configure(text=t(lang, "download_btn"))
            self.select_all_btn.configure(text=t(lang, "select_all"))
            self.select_none_btn.configure(text=t(lang, "select_none"))
            self.footer_label.configure(text=f"yadisk-downloader {__version__} by {APP_AUTHOR} ·")
            self.status_label.configure(text=t(lang, "ready"))
            self._update_path_preview()
            # Rebuild choice menus with translated sentinel values
            self.folder_menu.configure(values=[t(lang, "all_folders")] + self.folders)
            self.type_menu.configure(values=[t(lang, "all_types")] + FILE_TYPES)
            self.preset_menu.configure(
                values=[t(lang, "no_conversion")]
                + [f"{p.name} — {p.description}" for p in PRESETS.values()],
            )
            # Refresh placeholders
            self.canvas.itemconfigure(self.placeholder_id, text=t(lang, "placeholder_list"))
            if self._link_placeholder_active:
                self.link_entry.delete(0, "end")
                self.link_entry.insert(0, t(lang, "link_placeholder"))

        def _update_path_preview(self, *args):
            output = self.output_entry.get().strip() or "./downloads"
            self.path_label.configure(
                text=t(self.language, "path_preview").format(output=output),
            )

        def _set_link_placeholder(self, event=None):
            if not self.link_entry.get():
                self._link_placeholder_active = True
                self.link_entry.configure(foreground=TEXT_MUTED)
                self.link_entry.insert(0, t(self.language, "link_placeholder"))

        def _clear_link_placeholder(self, event=None):
            if self._link_placeholder_active:
                self._link_placeholder_active = False
                self.link_entry.delete(0, "end")
                self.link_entry.configure(foreground="#212529")

        def _get_link(self) -> str:
            if self._link_placeholder_active:
                return ""
            return self.link_entry.get().strip()

        def _paste_from_clipboard(self, event=None):
            try:
                self._clear_link_placeholder()
                self.link_entry.delete(0, "end")
                # Try multiple methods to get clipboard content
                text = ""
                try:
                    text = self.clipboard_get()
                except Exception:
                    pass
                if not text:
                    try:
                        import subprocess
                        if os.name == 'nt':  # Windows
                            result = subprocess.run(['powershell', '-command', 'Get-Clipboard'],
                                                      capture_output=True, text=True, timeout=5)
                            text = result.stdout.strip()
                    except Exception:
                        pass
                if text:
                    self.link_entry.insert(0, text)
                return "break"
            except Exception:
                pass

        def _show_context_menu(self, event):
            lang = self.language
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label=t(lang, "cut"), command=lambda: self.link_entry.event_generate("<<Cut>>"))
            menu.add_command(label=t(lang, "copy"), command=lambda: self.link_entry.event_generate("<<Copy>>"))
            menu.add_command(label=t(lang, "paste"), command=self._paste_from_clipboard)
            menu.add_separator()
            menu.add_command(label=t(lang, "select_all_menu"), command=lambda: self.link_entry.event_generate("<<SelectAll>>"))
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        def _browse_output(self):
            path = filedialog.askdirectory()
            if path:
                self.output_entry.delete(0, "end")
                self.output_entry.insert(0, path)
                self.output_var.set(path)

        def _scan(self):
            lang = self.language
            url = self._get_link()
            if not url:
                self.status_label.configure(text=t(lang, "enter_link"))
                return
            self.scan_btn.configure(state="disabled", text=t(lang, "scanning"))
            self.status_label.configure(text=t(lang, "scanning"))
            threading.Thread(target=self._scan_thread, args=(url,), daemon=True).start()

        def _scan_thread(self, url):
            lang = self.language
            try:
                self.files = list_files(url)
                self.folders = sorted({f["folder"] for f in self.files if f["folder"]})
            except Exception as e:
                error_msg = t(lang, "error_prefix").format(e)
                self.after(0, lambda: (
                    messagebox.showerror(t(lang, "title"), error_msg),
                    self.status_label.configure(text=error_msg),
                    self.scan_btn.configure(state="normal", text=t(lang, "scan_btn")),
                ))
                return
            self.after(0, self._update_file_list)

        def _update_file_list(self):
            lang = self.language
            for cb in self.file_checkboxes:
                cb.destroy()
            self.file_checkboxes.clear()

            ftype = self.type_var.get()
            if not ftype or ftype == t(lang, "all_types"):
                shown = self.files
            else:
                shown = [f for f in self.files if f.get("file_type") == ftype]

            all_folders = t(lang, "all_folders")
            self.folder_menu.configure(values=[all_folders] + self.folders)

            for f in shown:
                size = format_size(f["size"]) if f["size"] else "?"
                folder = f["folder"]
                display = f"[{folder}] {f['name']}  ({size})" if folder else f"{f['name']}  ({size})"
                var = tk.BooleanVar(value=True)
                cb = ttk.Checkbutton(self.file_scroll, text=display, variable=var)
                cb.pack(fill="x", anchor="w", padx=5, pady=2)
                cb.file_data = f
                cb.var = var
                self.file_checkboxes.append(cb)

            if shown:
                self.canvas.itemconfigure(self.placeholder_id, state="hidden")
                self.scrollbar.pack(side="right", fill="y")
                total = format_size(sum(f["size"] for f in shown))
                self.status_label.configure(text=t(lang, "found_files").format(len(shown), total))
            else:
                self.scrollbar.pack_forget()
                self.canvas.itemconfigure(self.placeholder_id, state="normal")
                if self.files:
                    self.status_label.configure(text=t(lang, "found_files").format(0, "0 B"))
            self.scan_btn.configure(state="normal", text=t(lang, "scan_btn"))

        def _select_all(self):
            for cb in self.file_checkboxes:
                cb.var.set(True)

        def _select_none(self):
            for cb in self.file_checkboxes:
                cb.var.set(False)

        def _get_preset_name(self):
            val = self.preset_var.get()
            if val == t(self.language, "no_conversion"):
                return None
            return val.split(" — ")[0]

        def _download(self):
            lang = self.language
            url = self._get_link()
            if not url:
                self.status_label.configure(text=t(lang, "enter_link"))
                return
            selected = [cb.file_data for cb in self.file_checkboxes if cb.var.get()]
            if not selected:
                self.status_label.configure(text=t(lang, "no_files_selected"))
                return
            output = self.output_entry.get().strip() or "./downloads"
            resolution = self.res_var.get()
            preset = self._get_preset_name()
            delete_original = self.delete_var.get()
            self.cancel_event.clear()
            self.download_btn.configure(
                state="normal", text=t(lang, "cancel"),
                bootstyle="danger", command=self._cancel_download,
            )
            threading.Thread(
                target=self._download_thread,
                args=(url, selected, output, resolution, preset, delete_original),
                daemon=True,
            ).start()

        def _cancel_download(self):
            self.cancel_event.set()

        def _restore_download_btn(self, lang):
            self.download_btn.configure(
                state="normal", text=t(lang, "download_btn"),
                bootstyle="success", command=self._download,
            )

        def _download_thread(self, url, files, output, resolution, preset, delete_original):
            lang = self.language
            ffmpeg = find_ffmpeg()
            if not ffmpeg:
                msg = t(lang, "ffmpeg_missing")
                self.after(0, lambda: (
                    messagebox.showerror(t(lang, "title"), msg),
                    self.status_label.configure(text=msg),
                    self._restore_download_btn(lang),
                ))
                return

            from .core.browser import collect_m3u8_urls
            from .plugins.base import FileInfo

            # Collect m3u8 URLs for videos
            collecting = t(lang, "collecting_urls")
            self.after(0, lambda: self.status_label.configure(text=collecting))
            m3u8_map = collect_m3u8_urls(url, files, resolution, lambda c, t_, n="": None)

            total = len(files)
            success = 0
            failed = 0
            cancelled = False

            for i, f in enumerate(files, 1):
                if self.cancel_event.is_set():
                    cancelled = True
                    break

                ft = f.get("file_type", "other")
                folder = f["folder"]
                dest = os.path.join(output, folder, f["name"]) if folder else os.path.join(output, f["name"])

                def progress_cb(downloaded, total_bytes, _i=i, _name=f["name"]):
                    if self.cancel_event.is_set():
                        raise RuntimeError("cancelled")
                    frac = downloaded / total_bytes if total_bytes else 0.0
                    overall = (_i - 1 + frac) / total * 100
                    text = t(lang, "downloading_overall").format(_i, total, _name[:40], frac * 100)
                    self.after(0, lambda s=text, p=overall: (
                        self.status_label.configure(text=s),
                        self.progress.configure(value=p),
                    ))

                download_url = get_download_url(url, f["path"])
                file_info = FileInfo(
                    name=f["name"],
                    path=f["path"],
                    size=f["size"],
                    file_type=ft,
                    folder=folder or None,
                    download_url=download_url,
                    m3u8_url=m3u8_map.get(f["path"]) if ft == "video" else None,
                )

                dest_path = Path(dest)
                os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)

                ok_dl = False
                size = 0

                try:
                    success_download, size = download_file(
                        file_info=file_info,
                        dest=dest_path,
                        progress_callback=progress_cb,
                        resume=True,
                        workers=4,
                        ffmpeg_path=ffmpeg,
                    )
                    ok_dl = success_download
                except Exception as e:
                    if str(e) == "cancelled":
                        cancelled = True
                        break
                    print(f"Download error: {e}")
                    ok_dl = False

                if ok_dl:
                    success += 1
                    if preset and ft == "video":
                        conv_out = get_output_path(dest, preset)
                        ok_conv, _ = convert(ffmpeg, dest, conv_out, preset)
                        if ok_conv and delete_original:
                            os.remove(dest)
                else:
                    failed += 1

            if cancelled:
                done_text = t(lang, "cancelled_status").format(success)
            else:
                done_text = t(lang, "done_status").format(success, failed)
            self.after(0, lambda: (
                self.status_label.configure(text=done_text),
                self.progress.configure(value=0 if cancelled else 100),
                self._restore_download_btn(lang),
            ))


def run_gui():
    if ttk is None:
        print("ERROR: ttkbootstrap is not installed.")
        print("Install it with: pip install ttkbootstrap")
        return
    app = App()
    app.mainloop()
