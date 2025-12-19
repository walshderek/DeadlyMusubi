#!/usr/bin/env python3
# Image Culler & Cropper — fast thumbs + live crop size + silent saves
#
# Adds:
# - NO "Saved" OK popup after saving
# - Non-blocking status text briefly shows save path
#
# Keeps:
# - Instant thumbnail grid
# - Size presets
# - Live crop WxH display
# - Everything else unchanged

import os
import sys
import json
import threading
import subprocess
import queue
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageTk, UnidentifiedImageError

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

APP_STATE_PATH = str(Path.home() / "image_culler_state.json")
SCRIPT_PATH = str(Path(__file__).with_name("image_culler_cropper.py"))


class ImageCullerApp(tk.Tk):
    def __init__(self, start_folder=None):
        super().__init__()
        self.title("Image Culler & Cropper")
        self.geometry("1280x860")
        self.minsize(1000, 620)

        self.supported_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".gif"}

        # practical presets only
        self.thumb_sizes = [100, 120, 140, 160, 180, 200, 220]
        self.thumb_size = 180
        self.columns = 5

        # caches & button map
        self.thumb_cache = {}     # path -> PhotoImage
        self.thumb_images = []    # keep refs alive
        self.thumb_buttons = {}   # path -> ttk.Button
        self.thumb_frames = {}    # path -> ttk.Frame (cell)

        self.current_folder = None
        self.images = []
        self.current_path = None
        self.preview_img = None
        self.preview_tk = None
        self.preview_scale = 1.0
        self.crop_rect = None
        self.crop_start = None
        self.save_dir = None

        # background loading
        self.stop_loading = threading.Event()
        self.load_gen = 0
        self.thumb_queue = queue.Queue()

        # safe worker pool (PIL only)
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.queue_poller_id = None

        # for temporary status messages
        self._status_after_id = None
        self._base_status_text = ""

        self._load_state()
        self._build_ui()

        target = start_folder or self.current_folder
        if target and Path(target).exists():
            self.load_folder(target)

    # ================== UI ===================
    def _build_ui(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=8, pady=6)

        ttk.Button(toolbar, text="Open Folder…", command=self.choose_folder).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="Open Containing Folder", command=self.open_containing_folder).pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(toolbar, text="Thumbnail size").pack(side=tk.LEFT)

        self.size_var = tk.IntVar(value=self.thumb_size)
        self.size_combo = ttk.Combobox(
            toolbar,
            textvariable=self.size_var,
            values=self.thumb_sizes,
            width=5,
            state="readonly"
        )
        self.size_combo.pack(side=tk.LEFT, padx=8)
        self.size_combo.bind("<<ComboboxSelected>>", self.on_thumb_size_change)

        self.size_label = ttk.Label(toolbar, text=f"{self.thumb_size}px")
        self.size_label.pack(side=tk.LEFT, padx=(0, 12))

        ttk.Button(toolbar, text="Crop Selection", command=self.apply_crop).pack(side=tk.LEFT, padx=8)
        ttk.Button(toolbar, text="Save As…", command=self.save_as_dialog).pack(side=tk.LEFT, padx=8)
        ttk.Button(toolbar, text="Save to Keepers", command=self.save_to_keepers).pack(side=tk.LEFT, padx=8)
        ttk.Button(toolbar, text="Save to Subfolder…", command=self.save_to_subfolder_prompt).pack(side=tk.LEFT, padx=8)

        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        self.canvas = tk.Canvas(left, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)

        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        right = ttk.Frame(paned)
        paned.add(right, weight=2)

        self.preview_canvas = tk.Canvas(right, bg="#111111", cursor="tcross")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self.preview_canvas.bind("<ButtonPress-1>", self.on_preview_press)
        self.preview_canvas.bind("<B1-Motion>", self.on_preview_drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_preview_release)
        self.preview_canvas.bind("<Configure>", lambda e: self.render_preview())

        status = ttk.Frame(self)
        status.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=4)
        self.info_label = ttk.Label(status, text="")
        self.info_label.pack(side=tk.LEFT)
        self.file_label = ttk.Label(status, text="", foreground="#888888")
        self.file_label.pack(side=tk.RIGHT)

    # ============== State ==============
    def _load_state(self):
        try:
            if os.path.exists(APP_STATE_PATH):
                with open(APP_STATE_PATH, "r") as f:
                    state = json.load(f)
                self.current_folder = state.get("current_folder")
                self.thumb_size = int(state.get("thumb_size", 180))
                if self.thumb_size not in self.thumb_sizes:
                    self.thumb_size = 180
                self.save_dir = state.get("save_dir")
        except Exception:
            pass

    def _save_state(self):
        try:
            state = {
                "current_folder": self.current_folder,
                "thumb_size": self.thumb_size,
                "save_dir": self.save_dir,
            }
            with open(APP_STATE_PATH, "w") as f:
                json.dump(state, f)
        except Exception:
            pass

    # ============== Status helper ==============
    def _set_temp_status(self, text, ms=2000):
        """Show a temporary status message on bottom-left, non-blocking."""
        if not self._base_status_text:
            self._base_status_text = self.info_label.cget("text")

        self.info_label.config(text=text)

        if self._status_after_id:
            try:
                self.after_cancel(self._status_after_id)
            except Exception:
                pass

        def restore():
            self.info_label.config(text=self._base_status_text)
            self._status_after_id = None

        self._status_after_id = self.after(ms, restore)

    # ============== Folder & thumbs ==============
    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.current_folder or str(Path.home()))
        if folder:
            self.load_folder(folder)

    def load_folder(self, folder):
        self.stop_loading.set()
        self.load_gen += 1
        gen = self.load_gen

        while not self.thumb_queue.empty():
            try:
                self.thumb_queue.get_nowait()
            except Exception:
                break

        self.stop_loading.clear()

        self.current_folder = folder
        self._save_state()

        self.images = [str(p) for p in Path(folder).iterdir() if p.suffix.lower() in self.supported_exts]
        self.images.sort()
        self.update_info()

        for w in self.inner.winfo_children():
            w.destroy()

        self.thumb_cache.clear()
        self.thumb_images.clear()
        self.thumb_buttons.clear()
        self.thumb_frames.clear()

        self.render_thumbs()

        for path in self.images:
            self.executor.submit(self._make_thumb_task, path, self.thumb_size, gen)

        if self.queue_poller_id:
            self.after_cancel(self.queue_poller_id)
        self._poll_thumb_queue(gen)

    def render_thumbs(self):
        size = self.thumb_size
        cell = size + 8

        for idx, path in enumerate(self.images):
            row = idx // self.columns
            col = idx % self.columns

            frame = ttk.Frame(self.inner)
            frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            frame.config(width=cell, height=cell)
            frame.grid_propagate(False)

            btn = ttk.Button(frame, text=Path(path).name, command=lambda p=path: self.load_preview(p))
            btn.place(relx=0.5, rely=0.5, anchor="center", width=size, height=size)

            self.thumb_frames[path] = frame
            self.thumb_buttons[path] = btn

        for i in range(self.columns):
            self.inner.grid_columnconfigure(i, weight=0, minsize=cell, uniform="thumbcol")

    def _make_thumb_task(self, path, size, gen):
        if self.stop_loading.is_set() or gen != self.load_gen:
            return
        try:
            im = Image.open(path)
            im = self._ensure_static_frame(im)
            im.thumbnail((size, size), Image.Resampling.LANCZOS)
            self.thumb_queue.put((path, im, gen))
        except UnidentifiedImageError:
            return
        except Exception:
            return

    def _poll_thumb_queue(self, gen):
        applied = 0
        N = 25

        while applied < N:
            try:
                path, pil_img, item_gen = self.thumb_queue.get_nowait()
            except queue.Empty:
                break

            if item_gen != self.load_gen or gen != self.load_gen:
                continue

            btn = self.thumb_buttons.get(path)
            if btn and pil_img:
                tkimg = ImageTk.PhotoImage(pil_img)
                btn.configure(image=tkimg, text="")
                self.thumb_cache[path] = tkimg
                self.thumb_images.append(tkimg)

            applied += 1

        if gen == self.load_gen and not self.stop_loading.is_set():
            self.queue_poller_id = self.after(35, lambda: self._poll_thumb_queue(gen))

    def _ensure_static_frame(self, im: Image.Image) -> Image.Image:
        try:
            if getattr(im, "is_animated", False):
                im.seek(0)
            return im.convert("RGB") if im.mode not in ("RGB", "RGBA") else im.copy()
        except Exception:
            return im

    def on_thumb_size_change(self, _event=None):
        val = int(self.size_var.get())
        if val != self.thumb_size:
            self.thumb_size = val
            self.size_label.config(text=f"{self.thumb_size}px")
            if self.current_folder:
                self.load_folder(self.current_folder)

    def update_info(self):
        count = len(self.images)
        folder_name = Path(self.current_folder).name if self.current_folder else ""
        text = f"{folder_name} — {count} image(s)"
        self.info_label.config(text=text)
        self._base_status_text = text  # keep base status updated

    # ============== Preview & crop ==============
    def load_preview(self, path):
        try:
            im = Image.open(path)
            im = self._ensure_static_frame(im)
            self.preview_img = im
            self.current_path = path
            self.crop_rect = None
            self.render_preview()
            self.file_label.config(text=f"{Path(path).name} — {im.width}×{im.height}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image:\n{e}")

    def render_preview(self):
        self.preview_canvas.delete("all")
        if not self.preview_img:
            return
        cw = self.preview_canvas.winfo_width()
        ch = self.preview_canvas.winfo_height()
        if cw < 10 or ch < 10:
            self.after(50, self.render_preview)
            return
        iw, ih = self.preview_img.size
        scale = min(cw / iw, ch / ih)
        self.preview_scale = scale
        disp = self.preview_img.resize((int(iw * scale), int(ih * scale)), Image.Resampling.LANCZOS)
        self.preview_tk = ImageTk.PhotoImage(disp)
        self.preview_canvas.create_image(cw // 2, ch // 2, image=self.preview_tk, anchor="center", tags="img")
        if self.crop_rect:
            x0, y0, x1, y1 = self.crop_rect
            self.preview_canvas.create_rectangle(x0, y0, x1, y1, outline="#00FF88", width=2, tags="crop")

    def on_preview_press(self, event):
        if not self.preview_img:
            return
        self.crop_start = (event.x, event.y)
        self.crop_rect = (event.x, event.y, event.x, event.y)
        self.render_preview()
        self._update_live_crop_label()

    def on_preview_drag(self, event):
        if not self.crop_start:
            return
        x0, y0 = self.crop_start
        x1, y1 = event.x, event.y
        self.crop_rect = (x0, y0, x1, y1)
        self.render_preview()
        self._update_live_crop_label()

    def on_preview_release(self, event):
        self._update_live_crop_label(final=True)

    def _update_live_crop_label(self, final=False):
        if not (self.preview_img and self.current_path and self.crop_rect):
            return
        box = self._calc_image_crop_box()
        if not box:
            im = self.preview_img
            self.file_label.config(text=f"{Path(self.current_path).name} — {im.width}×{im.height}")
            return
        w = box[2] - box[0]
        h = box[3] - box[1]
        im = self.preview_img
        self.file_label.config(
            text=f"{Path(self.current_path).name} — {im.width}×{im.height} (crop {w}×{h})"
        )

    def _calc_image_crop_box(self):
        if not (self.preview_img and self.crop_rect):
            return None
        x0, y0, x1, y1 = self.crop_rect
        if x1 < x0:
            x0, x1 = x1, x0
        if y1 < y0:
            y0, y1 = y1, y0
        scale = self.preview_scale
        cw = self.preview_canvas.winfo_width()
        ch = self.preview_canvas.winfo_height()
        iw, ih = self.preview_img.size
        disp_w, disp_h = int(iw * scale), int(ih * scale)
        left = (cw - disp_w) // 2
        top = (ch - disp_h) // 2
        x0i = int((x0 - left) / scale)
        y0i = int((y0 - top) / scale)
        x1i = int((x1 - left) / scale)
        y1i = int((y1 - top) / scale)
        x0i = max(0, min(iw, x0i))
        x1i = max(0, min(iw, x1i))
        y0i = max(0, min(ih, y0i))
        y1i = max(0, min(ih, y1i))
        if x1i <= x0i or y1i <= y0i:
            return None
        return (x0i, y0i, x1i, y1i)

    def apply_crop(self):
        box = self._calc_image_crop_box()
        if not box:
            messagebox.showinfo("Crop", "Draw a rectangle on the preview first (click and drag).")
            return
        try:
            cropped = self.preview_img.crop(box)
            self.preview_img = cropped
            self.crop_rect = None
            self.render_preview()
            self.file_label.config(text=f"{Path(self.current_path).name} — {cropped.width}×{cropped.height} (cropped)")
        except Exception as e:
            messagebox.showerror("Error", f"Crop failed:\n{e}")

    # ============== Saving ==============
    def _default_filename(self):
        if not self.current_path:
            return "cropped.jpg"
        p = Path(self.current_path)
        return f"{p.stem}_cropped{p.suffix}"

    def save_as_dialog(self):
        if not self.preview_img:
            messagebox.showinfo("Save", "Open an image and make a selection or crop first.")
            return
        initialdir = self.save_dir or (self.current_folder or str(Path.home()))
        initialfile = self._default_filename()
        filetypes = [
            ("JPEG", "*.jpg;*.jpeg"),
            ("PNG", "*.png"),
            ("WEBP", "*.webp"),
            ("TIFF", "*.tif;*.tiff"),
            ("BMP", "*.bmp"),
        ]
        path = filedialog.asksaveasfilename(defaultextension=Path(initialfile).suffix,
                                            initialdir=initialdir,
                                            initialfile=initialfile,
                                            filetypes=filetypes)
        if not path:
            return
        self._do_save(Path(path))

    def save_to_keepers(self):
        if not self.preview_img or not self.current_folder:
            messagebox.showinfo("Save", "Open a folder and image first.")
            return
        keep = Path(self.current_folder) / "Keepers"
        keep.mkdir(exist_ok=True)
        self._do_save(keep / self._default_filename())

    def save_to_subfolder_prompt(self):
        if not self.preview_img or not self.current_folder:
            messagebox.showinfo("Save", "Open a folder and image first.")
            return
        name = simpledialog.askstring("Subfolder", "Save to subfolder name:", initialvalue="Keepers", parent=self)
        if not name:
            return
        sub = Path(self.current_folder) / name
        sub.mkdir(parents=True, exist_ok=True)
        self._do_save(sub / self._default_filename())

    def _do_save(self, path: Path):
        try:
            ext = path.suffix.lower()
            params = {}
            if ext in {".jpg", ".jpeg"}:
                params["quality"] = 95
            self.preview_img.save(str(path), **params)
            self.save_dir = str(path.parent)
            self._save_state()

            # NO OK POPUP. Just a short status flash.
            self._set_temp_status(f"Saved: {path}")

        except Exception as e:
            messagebox.showerror("Error", f"Save failed:\n{e}")

    def open_containing_folder(self):
        if not self.current_folder:
            return
        try:
            if os.name == "nt":
                os.startfile(self.current_folder)
            else:
                subprocess.Popen(["xdg-open", self.current_folder])
        except Exception:
            pass

    # ---- Mousewheel ----
    def _on_mousewheel(self, event):
        if event.delta:
            step = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(step * 3, "units")

    def _bind_mousewheel(self, *_):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-3, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(3, "units"))

    def _unbind_mousewheel(self, *_):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")


def write_script_file():
    try:
        code = open(__file__, "r", encoding="utf-8").read()
        with open(SCRIPT_PATH, "w", encoding="utf-8") as f:
            f.write(code)
    except Exception:
        pass


if __name__ == "__main__":
    write_script_file()
    start = sys.argv[1] if len(sys.argv) > 1 else None
    app = ImageCullerApp(start_folder=start)
    app.mainloop()
