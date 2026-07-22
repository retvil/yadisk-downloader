"""GUI interface for yadisk-downloader using customtkinter."""

import os
import threading
import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk

from .core.api import list_files, list_folders
from .core.browser import collect_m3u8_urls
from .core.converter import PRESETS, convert, get_output_path
from .core.downloader import download
from .utils import find_ffmpeg, format_size


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Yandex Disk Video Downloader")
        self.geometry("900x750")
        self.minsize(800, 600)

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.files = []
        self.folders = []
        self.file_checkboxes = []

        self._build_ui()

    def _build_ui(self):
        # Main container
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=15, pady=15)

        # --- Link ---
        link_frame = ctk.CTkFrame(main, fg_color="transparent")
        link_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(link_frame, text="Public link:").pack(side="left", padx=(0, 5))
        self.link_entry = ctk.CTkEntry(link_frame, placeholder_text="https://disk.yandex.ru/d/...")
        self.link_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.scan_btn = ctk.CTkButton(link_frame, text="Scan", width=80, command=self._scan)
        self.scan_btn.pack(side="right")

        # --- Settings row ---
        settings_frame = ctk.CTkFrame(main, fg_color="transparent")
        settings_frame.pack(fill="x", pady=(0, 10))

        # Resolution
        res_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        res_frame.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(res_frame, text="Resolution:").pack(side="left", padx=(0, 5))
        self.res_var = ctk.StringVar(value="720p")
        for res in ["240p", "360p", "480p", "720p", "1080p"]:
            ctk.CTkRadioButton(res_frame, text=res, variable=self.res_var, value=res).pack(side="left", padx=2)

        # Output dir
        out_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        out_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(out_frame, text="Output:").pack(side="left", padx=(0, 5))
        self.output_entry = ctk.CTkEntry(out_frame, placeholder_text="./downloads")
        self.output_entry.insert(0, "./downloads")
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(out_frame, text="...", width=35, command=self._browse_output).pack(side="right")

        # --- Folder + Preset row ---
        row2 = ctk.CTkFrame(main, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 10))

        # Folder
        folder_frame = ctk.CTkFrame(row2, fg_color="transparent")
        folder_frame.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(folder_frame, text="Folder:").pack(side="left", padx=(0, 5))
        self.folder_var = ctk.StringVar(value="All folders")
        self.folder_menu = ctk.CTkOptionMenu(folder_frame, variable=self.folder_var, values=["All folders"])
        self.folder_menu.pack(side="left")

        # Preset
        preset_frame = ctk.CTkFrame(row2, fg_color="transparent")
        preset_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(preset_frame, text="Convert:").pack(side="left", padx=(0, 5))
        self.preset_var = ctk.StringVar(value="No conversion")
        preset_values = ["No conversion"] + [f"{p.name} — {p.description}" for p in PRESETS.values()]
        self.preset_menu = ctk.CTkOptionMenu(preset_frame, variable=self.preset_var, values=preset_values)
        self.preset_menu.pack(side="left", fill="x", expand=True)

        self.delete_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(row2, text="Delete original", variable=self.delete_var).pack(side="right", padx=(10, 0))

        # --- Buttons ---
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))

        self.download_btn = ctk.CTkButton(btn_frame, text="Download Selected", command=self._download)
        self.download_btn.pack(side="left")

        ctk.CTkButton(btn_frame, text="Select All", width=90, command=self._select_all).pack(side="right", padx=(5, 0))
        ctk.CTkButton(btn_frame, text="Select None", width=90, command=self._select_none).pack(side="right")

        # --- File list ---
        list_frame = ctk.CTkFrame(main)
        list_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.file_scroll = ctk.CTkScrollableFrame(list_frame)
        self.file_scroll.pack(fill="both", expand=True)

        # --- Status ---
        self.status_label = ctk.CTkLabel(main, text="Ready", anchor="w")
        self.status_label.pack(fill="x")

        self.progress = ctk.CTkProgressBar(main)
        self.progress.pack(fill="x", pady=(5, 0))
        self.progress.set(0)

    def _browse_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, path)

    def _scan(self):
        url = self.link_entry.get().strip()
        if not url:
            self.status_label.configure(text="Enter a public link first")
            return

        self.scan_btn.configure(state="disabled", text="Scanning...")
        self.status_label.configure(text="Scanning files...")
        threading.Thread(target=self._scan_thread, args=(url,), daemon=True).start()

    def _scan_thread(self, url):
        try:
            self.files = list_files(url)
            self.folders = sorted(set(f["folder"] for f in self.files if f["folder"]))
        except Exception as e:
            self.after(0, lambda: self.status_label.configure(text=f"Error: {e}"))
            self.after(0, lambda: self.scan_btn.configure(state="normal", text="Scan"))
            return

        self.after(0, self._update_file_list)

    def _update_file_list(self):
        # Clear old checkboxes
        for cb in self.file_checkboxes:
            cb.destroy()
        self.file_checkboxes.clear()

        # Update folder dropdown
        values = ["All folders"] + self.folders
        self.folder_menu.configure(values=values)
        self.folder_var.set("All folders")

        # Populate file list
        for f in self.files:
            size = format_size(f["size"]) if f["size"] else "?"
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(
                self.file_scroll,
                text=f"{f['name']}  ({size})",
                variable=var,
            )
            cb.pack(fill="x", anchor="w", padx=5, pady=2)
            cb.file_data = f
            cb.var = var
            self.file_checkboxes.append(cb)

        total = format_size(sum(f["size"] for f in self.files))
        self.status_label.configure(text=f"Found {len(self.files)} files ({total})")
        self.scan_btn.configure(state="normal", text="Scan")

    def _select_all(self):
        for cb in self.file_checkboxes:
            cb.var.set(True)

    def _select_none(self):
        for cb in self.file_checkboxes:
            cb.var.set(False)

    def _get_preset_name(self) -> str | None:
        val = self.preset_var.get()
        if val == "No conversion":
            return None
        return val.split(" — ")[0]

    def _download(self):
        url = self.link_entry.get().strip()
        if not url:
            self.status_label.configure(text="Enter a public link first")
            return

        selected = [cb.file_data for cb in self.file_checkboxes if cb.var.get()]
        if not selected:
            self.status_label.configure(text="No files selected")
            return

        output = self.output_entry.get().strip() or "./downloads"
        resolution = self.res_var.get()
        preset = self._get_preset_name()
        delete_original = self.delete_var.get()

        self.download_btn.configure(state="disabled")
        threading.Thread(
            target=self._download_thread,
            args=(url, selected, output, resolution, preset, delete_original),
            daemon=True,
        ).start()

    def _download_thread(self, url, files, output, resolution, preset, delete_original):
        ffmpeg = find_ffmpeg()
        if not ffmpeg:
            self.after(0, lambda: self.status_label.configure(text="ERROR: ffmpeg not found"))
            self.after(0, lambda: self.download_btn.configure(state="normal"))
            return

        # Collect m3u8 URLs
        self.after(0, lambda: self.status_label.configure(text="Collecting video URLs..."))

        def progress_cb(current, total, name):
            self.after(0, lambda c=current, t=total, n=name: (
                self.status_label.configure(text=f"[{c}/{t}] {n[:50]}..."),
                self.progress.set(c / t),
            ))

        m3u8_map = collect_m3u8_urls(url, files, resolution, progress_cb)

        # Download
        total = len(files)
        success = 0
        failed = 0

        for i, f in enumerate(files, 1):
            m3u8 = m3u8_map.get(f["path"])
            if not m3u8:
                failed += 1
                continue

            folder = f["folder"]
            dest = os.path.join(output, folder, f["name"]) if folder else os.path.join(output, f["name"])

            self.after(0, lambda c=i, t=total, n=f["name"]: (
                self.status_label.configure(text=f"[{c}/{t}] Downloading {n[:40]}..."),
                self.progress.set(c / t),
            ))

            ok, size = download(ffmpeg, m3u8, dest)
            if ok:
                success += 1

                # Convert
                if preset:
                    conv_out = get_output_path(dest, preset)
                    ok_conv, _ = convert(ffmpeg, dest, conv_out, preset)
                    if ok_conv and delete_original:
                        os.remove(dest)
            else:
                failed += 1

        self.after(0, lambda: (
            self.status_label.configure(text=f"Done! Success: {success}, Failed: {failed}"),
            self.progress.set(1.0),
            self.download_btn.configure(state="normal"),
        ))


def run_gui():
    app = App()
    app.mainloop()
