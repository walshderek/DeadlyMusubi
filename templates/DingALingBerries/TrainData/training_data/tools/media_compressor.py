import os
import sys
import json
import math
import threading
import subprocess
import queue as queue_module
import tempfile
import time
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ------------- CONFIG / CONSTANTS -------------

# Default target size (MB) that is safely under Discord's 10 MB limit.
DEFAULT_TARGET_MB = 9.4  # 9.4 * 1024 * 1024 bytes ≈ 9.85 MiB, comfortably under 10 MB limit.

FFMPEG_BIN = "ffmpeg"
FFPROBE_BIN = "ffprobe"


# ------------- HELPER FUNCTIONS -------------


def bytes_from_mb(mb_value: float) -> int:
    return int(mb_value * 1024 * 1024)


def run_subprocess(cmd, capture_output=False):
    """
    Run a subprocess. If capture_output=True, return (returncode, stdout, stderr).
    """
    try:
        if capture_output:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            return proc.returncode, proc.stdout, proc.stderr
        else:
            proc = subprocess.run(cmd)
            return proc.returncode, "", ""
    except FileNotFoundError:
        raise RuntimeError(
            f"Could not find command: {cmd[0]}\n"
            "Make sure ffmpeg/ffprobe are installed and on your PATH."
        )


def probe_media(path):
    """
    Use ffprobe to get metadata: type, duration, width, height, fps, audio_bitrate.
    Returns a dict or raises RuntimeError.
    """
    cmd = [
        FFMPEG_BIN.replace("ffmpeg", "ffprobe") if FFMPEG_BIN != "ffmpeg" else FFPROBE_BIN,
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        path
    ]
    rc, out, err = run_subprocess(cmd, capture_output=True)
    if rc != 0:
        raise RuntimeError(f"ffprobe failed for {path}:\n{err}")

    info = json.loads(out)

    fmt = info.get("format", {})
    duration = fmt.get("duration", "0")
    try:
        duration = float(duration)
    except ValueError:
        duration = 0.0

    streams = info.get("streams", [])

    video_stream = None
    audio_stream = None

    for s in streams:
        if s.get("codec_type") == "video" and video_stream is None:
            video_stream = s
        elif s.get("codec_type") == "audio" and audio_stream is None:
            audio_stream = s

    if video_stream is not None:
        media_type = "video"
        width = int(video_stream.get("width", 0))
        height = int(video_stream.get("height", 0))

        # fps from r_frame_rate or avg_frame_rate
        fps_str = video_stream.get("avg_frame_rate") or video_stream.get("r_frame_rate") or "0/1"
        try:
            num, den = fps_str.split("/")
            fps = float(num) / float(den) if float(den) != 0 else 0.0
        except Exception:
            fps = 0.0
    else:
        media_type = "audio"
        width = height = 0
        fps = 0.0

    # audio bitrate (in bps)
    audio_bps = 0
    if audio_stream is not None:
        br = audio_stream.get("bit_rate")
        if br is not None:
            try:
                audio_bps = int(br)
            except ValueError:
                audio_bps = 0

    return {
        "type": media_type,
        "duration": duration,
        "width": width,
        "height": height,
        "fps": fps,
        "audio_bps": audio_bps,
    }


def get_unique_output_path(base_path, suffix, new_ext):
    """
    Return a non-existing path by appending suffix and optional increment.
    NEVER overwrites existing files.
    base_path: original path (with extension).
    suffix: string e.g. "_compressed"
    new_ext: ".mp3", ".mp4", ".gif"
    """
    folder, name = os.path.split(base_path)
    root, _old_ext = os.path.splitext(name)
    candidate = os.path.join(folder, root + suffix + new_ext)
    if not os.path.exists(candidate):
        return candidate

    # If already exists, add incrementing counter.
    counter = 2
    while True:
        candidate = os.path.join(folder, f"{root}{suffix}_{counter}{new_ext}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def ensure_even(value: int) -> int:
    # ffmpeg often wants even dimensions
    if value % 2 != 0:
        return value - 1 if value > 1 else 2
    return value


def compute_scaled_dimensions(src_w, src_h, max_dim):
    """
    Preserve aspect ratio, longest side = max_dim (or smaller if source is smaller).
    Returns (new_w, new_h).
    """
    if src_w <= 0 or src_h <= 0 or max_dim is None or max_dim <= 0:
        return src_w, src_h

    longest = max(src_w, src_h)
    if longest <= max_dim:
        # no scaling needed
        return src_w, src_h

    scale = max_dim / float(longest)
    new_w = int(round(src_w * scale))
    new_h = int(round(src_h * scale))
    new_w = ensure_even(new_w)
    new_h = ensure_even(new_h)
    return new_w, new_h


def parse_ffmpeg_time_to_seconds(timestr):
    """
    Parse ffmpeg time string like "00:01:23.45" to seconds (float).
    """
    try:
        parts = timestr.split(":")
        if len(parts) != 3:
            return 0.0
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    except Exception:
        return 0.0


def read_ffmpeg_progress(proc, duration, progress_callback, stop_flag):
    """
    Read ffmpeg stderr lines, extract 'time=' to estimate progress.
    Call progress_callback(percentage, time_seconds, raw_line).
    """
    time_pattern = re.compile(r"time=(\d+:\d+:\d+\.\d+)")
    while True:
        if stop_flag.is_set():
            break
        line = proc.stderr.readline()
        if not line:
            break

        line = line.strip()
        match = time_pattern.search(line)
        if match and duration > 0:
            t = parse_ffmpeg_time_to_seconds(match.group(1))
            pct = max(0.0, min(100.0, (t / duration) * 100.0))
            progress_callback(pct, t, line)
        else:
            # Still send raw lines in case they contain warnings/errors
            progress_callback(None, None, line)

    proc.wait()


def format_duration(seconds):
    """
    Format seconds as H:MM:SS or M:SS depending on length.
    """
    if seconds is None or seconds <= 0:
        return "00:00"
    total = int(round(seconds))
    m, s = divmod(total, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:d}:{m:02d}:{s:02d}"
    else:
        return f"{m:d}:{s:02d}"


# ------------- ENCODING FUNCTIONS -------------

def encode_audio_to_mp3(input_path, output_path, target_bytes, duration, progress_callback, stop_flag):
    total_bits = target_bytes * 8
    if duration <= 0:
        # Fallback to some arbitrary duration to avoid div-by-zero
        duration = 1.0
    bps = total_bits / duration  # bits per second
    # Avoid ridiculously low bitrates that ffmpeg might choke on.
    if bps < 8000:
        bps = 8000
    kbps = int(bps / 1000)

    cmd = [
        FFMPEG_BIN,
        "-y",
        "-i", input_path,
        "-vn",
        "-c:a", "libmp3lame",
        "-b:a", f"{kbps}k",
        output_path,
    ]

    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
    read_ffmpeg_progress(proc, duration, progress_callback, stop_flag)
    return proc.returncode


def encode_video_to_mp4(
    input_path,
    output_path,
    target_bytes,
    duration,
    src_info,
    max_dim,
    fps_override,
    two_pass,
    progress_callback,
    stop_flag
):
    total_bits = target_bytes * 8
    if duration <= 0:
        duration = 1.0

    total_bps = total_bits / duration

    # Audio bitrate: depend on source and target size.
    # We let audio have up to 25% of total, but not exceed source audio bitrate if known.
    src_audio_bps = src_info.get("audio_bps", 0) or 0
    max_audio_bps = total_bps * 0.25
    if src_audio_bps > 0:
        audio_bps = min(src_audio_bps, max_audio_bps)
    else:
        # If unknown, allocate 20% of total to audio.
        audio_bps = total_bps * 0.2

    if audio_bps < 8000:
        audio_bps = 8000

    video_bps = total_bps - audio_bps
    if video_bps < 20000:
        # Ensure some minimal video bitrate
        video_bps = 20000
        audio_bps = total_bps - video_bps
        if audio_bps < 8000:
            audio_bps = 8000

    video_kbps = int(video_bps / 1000)
    audio_kbps = int(audio_bps / 1000)

    # Scaling
    vf_filters = []
    src_w = src_info.get("width", 0)
    src_h = src_info.get("height", 0)
    if max_dim is not None and max_dim > 0 and src_w > 0 and src_h > 0:
        new_w, new_h = compute_scaled_dimensions(src_w, src_h, max_dim)
        if new_w > 0 and new_h > 0 and (new_w != src_w or new_h != src_h):
            vf_filters.append(f"scale={new_w}:{new_h}")

    # Combine filters
    vf_arg = None
    if vf_filters:
        vf_arg = ",".join(vf_filters)

    # FPS override - we use -r for output.
    fps_arg = None
    if fps_override is not None and fps_override > 0:
        fps_arg = str(fps_override)

    # Two-pass or one-pass
    if two_pass:
        # Passlog in temp dir
        passlogfile = os.path.join(
            tempfile.gettempdir(),
            f"compress_passlog_{os.getpid()}"
        )

        # First pass (video only, no audio)
        cmd1 = [
            FFMPEG_BIN,
            "-y",
            "-i", input_path,
            "-c:v", "libx264",
            "-b:v", f"{video_kbps}k",
            "-pass", "1",
            "-passlogfile", passlogfile,
            "-an",
        ]
        if vf_arg:
            cmd1.extend(["-vf", vf_arg])
        if fps_arg:
            cmd1.extend(["-r", fps_arg])

        # On Windows, discard output to NUL
        cmd1.extend([
            "-f", "mp4",
            "NUL" if os.name == "nt" else "/dev/null"
        ])

        proc1 = subprocess.Popen(cmd1, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
        read_ffmpeg_progress(proc1, duration, progress_callback, stop_flag)
        rc1 = proc1.returncode

        if rc1 != 0 or stop_flag.is_set():
            # Clean up pass logs
            for ext in (".log", "-0.log", ".log.mbtree"):
                try:
                    os.remove(passlogfile + ext)
                except OSError:
                    pass
            return rc1

        # Second pass (with audio)
        cmd2 = [
            FFMPEG_BIN,
            "-y",
            "-i", input_path,
            "-c:v", "libx264",
            "-b:v", f"{video_kbps}k",
            "-pass", "2",
            "-passlogfile", passlogfile,
            "-c:a", "aac",
            "-b:a", f"{audio_kbps}k",
        ]
        if vf_arg:
            cmd2.extend(["-vf", vf_arg])
        if fps_arg:
            cmd2.extend(["-r", fps_arg])

        cmd2.append(output_path)

        proc2 = subprocess.Popen(cmd2, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
        read_ffmpeg_progress(proc2, duration, progress_callback, stop_flag)
        rc2 = proc2.returncode

        # Clean up pass logs
        for ext in (".log", "-0.log", ".log.mbtree"):
            try:
                os.remove(passlogfile + ext)
            except OSError:
                pass

        return rc2

    else:
        # One-pass
        cmd = [
            FFMPEG_BIN,
            "-y",
            "-i", input_path,
            "-c:v", "libx264",
            "-b:v", f"{video_kbps}k",
            "-c:a", "aac",
            "-b:a", f"{audio_kbps}k",
        ]
        if vf_arg:
            cmd.extend(["-vf", vf_arg])
        if fps_arg:
            cmd.extend(["-r", fps_arg])

        cmd.append(output_path)

        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
        read_ffmpeg_progress(proc, duration, progress_callback, stop_flag)
        return proc.returncode


def encode_video_to_gif(
    input_path,
    output_path,
    target_bytes,
    duration,
    src_info,
    max_dim,
    fps_override,
    progress_callback,
    stop_flag
):
    """
    Best-effort high-quality GIF.
    Note: It's hard to guarantee exact file size with GIF, but we still respect
    max_dim and FPS to keep things reasonable.
    """
    src_w = src_info.get("width", 0)
    src_h = src_info.get("height", 0)

    new_w, new_h = src_w, src_h
    if max_dim is not None and max_dim > 0 and src_w > 0 and src_h > 0:
        new_w, new_h = compute_scaled_dimensions(src_w, src_h, max_dim)

    fps = fps_override or src_info.get("fps", 0.0)
    if fps <= 0:
        fps = 10.0  # fallback for GIF pacing

    # We use palettegen + paletteuse for better quality.
    palette_path = os.path.join(
        tempfile.gettempdir(),
        f"palette_{os.getpid()}.png"
    )

    # First pass: generate palette
    vf_parts = [f"fps={fps}"]
    if new_w > 0 and new_h > 0:
        vf_parts.append(f"scale={new_w}:{new_h}:flags=lanczos")
    vf_palette = ",".join(vf_parts) + ",palettegen"

    cmd1 = [
        FFMPEG_BIN,
        "-y",
        "-i", input_path,
        "-vf", vf_palette,
        palette_path
    ]
    proc1 = subprocess.Popen(cmd1, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
    read_ffmpeg_progress(proc1, duration, progress_callback, stop_flag)
    rc1 = proc1.returncode

    if rc1 != 0 or stop_flag.is_set():
        try:
            os.remove(palette_path)
        except OSError:
            pass
        return rc1

    # Second pass: use palette
    vf_use = f"fps={fps}"
    if new_w > 0 and new_h > 0:
        vf_use += f",scale={new_w}:{new_h}:flags=lanczos"
    vf_use += f"[x];[x][1:v]paletteuse"

    cmd2 = [
        FFMPEG_BIN,
        "-y",
        "-i", input_path,
        "-i", palette_path,
        "-lavfi", vf_use,
        output_path
    ]
    proc2 = subprocess.Popen(cmd2, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
    read_ffmpeg_progress(proc2, duration, progress_callback, stop_flag)
    rc2 = proc2.returncode

    try:
        os.remove(palette_path)
    except OSError:
        pass

    return rc2


# ------------- GUI APPLICATION -------------


class MediaCompressorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Compressor (Tkinter)")

        # Queue data: list of dicts with {path, info, size_bytes, status}
        self.queue_items = []

        # Threading / progress
        self.worker_thread = None
        self.stop_flag = threading.Event()
        self.log_queue = queue_module.Queue()
        self.is_running = False

        self._build_ui()
        self._start_log_pump()

    # -------- UI BUILD --------

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=5)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top: controls
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 5))

        # File buttons
        file_btns = ttk.Frame(controls_frame)
        file_btns.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_add_files = ttk.Button(file_btns, text="Add Files...", command=self.add_files)
        self.btn_add_files.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_remove_selected = ttk.Button(file_btns, text="Remove Selected", command=self.remove_selected)
        self.btn_remove_selected.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_clear_queue = ttk.Button(file_btns, text="Clear Queue", command=self.clear_queue)
        self.btn_clear_queue.pack(side=tk.LEFT)

        # Target size & options
        options_frame = ttk.Frame(controls_frame)
        options_frame.pack(side=tk.LEFT, padx=(10, 10))

        # Target size
        ttk.Label(options_frame, text="Target size (MB):").grid(row=0, column=0, sticky="e")
        self.target_size_var = tk.StringVar(value=str(DEFAULT_TARGET_MB))
        self.entry_target_size = ttk.Entry(options_frame, width=8, textvariable=self.target_size_var)
        self.entry_target_size.grid(row=0, column=1, sticky="w")

        # Video output format
        ttk.Label(options_frame, text="Video format:").grid(row=0, column=2, sticky="e", padx=(10, 0))
        self.video_format_var = tk.StringVar(value="MP4")
        self.combo_video_format = ttk.Combobox(
            options_frame,
            textvariable=self.video_format_var,
            values=["MP4", "GIF"],
            state="readonly",
            width=6
        )
        self.combo_video_format.grid(row=0, column=3, sticky="w")

        # Max dimension (longest side)
        ttk.Label(options_frame, text="Max dimension (longest side, px):").grid(row=1, column=0, sticky="e", pady=(5, 0))
        self.max_dim_var = tk.StringVar(value="")
        self.entry_max_dim = ttk.Entry(options_frame, width=8, textvariable=self.max_dim_var)
        self.entry_max_dim.grid(row=1, column=1, sticky="w", pady=(5, 0))

        # FPS override
        ttk.Label(options_frame, text="FPS override:").grid(row=1, column=2, sticky="e", padx=(10, 0), pady=(5, 0))
        self.fps_var = tk.StringVar(value="")
        self.entry_fps = ttk.Entry(options_frame, width=6, textvariable=self.fps_var)
        self.entry_fps.grid(row=1, column=3, sticky="w", pady=(5, 0))

        # 2-pass option
        self.two_pass_var = tk.IntVar(value=0)
        self.chk_two_pass = ttk.Checkbutton(
            options_frame,
            text="2-pass (MP4 only)",
            variable=self.two_pass_var
        )
        self.chk_two_pass.grid(row=2, column=0, columnspan=4, sticky="w", pady=(5, 0))

        # Start / Stop / Exit
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(side=tk.RIGHT, padx=(10, 0))

        self.btn_start = ttk.Button(buttons_frame, text="Start", command=self.start_processing)
        self.btn_start.pack(side=tk.TOP, fill=tk.X)

        self.btn_stop = ttk.Button(buttons_frame, text="Stop", command=self.stop_processing)
        self.btn_stop.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

        self.btn_exit = ttk.Button(buttons_frame, text="Exit", command=self.root.destroy)
        self.btn_exit.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))

        # Middle: Queue list
        queue_frame = ttk.LabelFrame(main_frame, text="Queue")
        queue_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 5))

        self.queue_listbox = tk.Listbox(queue_frame, height=8, activestyle="dotbox")
        self.queue_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_queue = ttk.Scrollbar(queue_frame, orient=tk.VERTICAL, command=self.queue_listbox.yview)
        scrollbar_queue.pack(side=tk.RIGHT, fill=tk.Y)
        self.queue_listbox.config(yscrollcommand=scrollbar_queue.set)

        # Bottom: Log
        log_frame = ttk.LabelFrame(main_frame, text="Log")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.text_log = tk.Text(log_frame, wrap="word", height=12)
        self.text_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_log = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.text_log.yview)
        scrollbar_log.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_log.config(yscrollcommand=scrollbar_log.set)

        # Make window reasonably sized
        self.root.minsize(900, 600)

    # -------- LOGGING --------

    def log(self, message):
        """
        Thread-safe log: put message into a queue; UI thread pulls it.
        """
        self.log_queue.put(message)

    def _start_log_pump(self):
        """
        Periodically flush log_queue into the Text widget.
        """
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.text_log.insert(tk.END, msg + "\n")
                self.text_log.see(tk.END)
        except queue_module.Empty:
            pass

        self.root.after(100, self._start_log_pump)

    # -------- QUEUE MANAGEMENT --------

    def add_files(self):
        if self.is_running:
            messagebox.showwarning("Busy", "Cannot add files while processing.")
            return

        paths = filedialog.askopenfilenames(
            title="Select media files",
            filetypes=[("Media files", "*.*"), ("All files", "*.*")]
        )
        if not paths:
            return

        for path in paths:
            if not os.path.isfile(path):
                continue
            try:
                info = probe_media(path)
                size_bytes = os.path.getsize(path)
                item = {
                    "path": path,
                    "info": info,
                    "size_bytes": size_bytes,
                    "status": "Pending",
                }
                self.queue_items.append(item)
                self._update_queue_listbox()
                self.log(f"Added to queue: {path} [{info['type']}]")
            except Exception as e:
                self.log(f"ERROR probing file: {path}\n  {e}")

    def _update_queue_listbox(self):
        self.queue_listbox.delete(0, tk.END)
        for item in self.queue_items:
            path = item["path"]
            status = item.get("status", "Pending")
            info = item["info"]
            mtype = info["type"]
            w = info.get("width", 0) or 0
            h = info.get("height", 0) or 0
            fps = info.get("fps", 0.0) or 0.0
            duration = info.get("duration", 0.0) or 0.0
            size_bytes = item.get("size_bytes", 0) or 0

            size_mb = size_bytes / (1024 * 1024) if size_bytes > 0 else 0.0
            dur_str = format_duration(duration)

            meta_parts = []
            if mtype == "video":
                if w > 0 and h > 0:
                    meta_parts.append(f"{w}x{h}")
                if fps > 0:
                    meta_parts.append(f"{fps:.2f}fps")
            # duration for both audio and video
            meta_parts.append(dur_str)
            # size
            meta_parts.append(f"{size_mb:.1f}MB")

            meta_str = ", ".join(meta_parts)

            display = f"{os.path.basename(path)} [{mtype}] {meta_str} - {status}"
            self.queue_listbox.insert(tk.END, display)

    def remove_selected(self):
        if self.is_running:
            messagebox.showwarning("Busy", "Cannot remove files while processing.")
            return

        sel = list(self.queue_listbox.curselection())
        if not sel:
            return
        sel.sort(reverse=True)
        for idx in sel:
            removed = self.queue_items.pop(idx)
            self.log(f"Removed from queue: {removed['path']}")
        self._update_queue_listbox()

    def clear_queue(self):
        if self.is_running:
            messagebox.showwarning("Busy", "Cannot clear queue while processing.")
            return
        self.queue_items.clear()
        self._update_queue_listbox()
        self.log("Queue cleared.")

    # -------- PROCESSING CONTROL --------

    def start_processing(self):
        if self.is_running:
            messagebox.showinfo("Processing", "Already running.")
            return

        if not self.queue_items:
            messagebox.showwarning("No files", "Queue is empty.")
            return

        # Read target size
        try:
            target_mb = float(self.target_size_var.get())
            if target_mb <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid target size", "Target size must be a positive number (MB).")
            return

        self.target_bytes = bytes_from_mb(target_mb)

        # max dimension
        max_dim_str = self.max_dim_var.get().strip()
        if max_dim_str:
            try:
                max_dim = int(max_dim_str)
                if max_dim <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid dimension", "Max dimension must be a positive integer.")
                return
        else:
            max_dim = None
        self.max_dim_value = max_dim

        # fps override
        fps_str = self.fps_var.get().strip()
        if fps_str:
            try:
                fps = float(fps_str)
                if fps <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid FPS", "FPS override must be a positive number.")
                return
        else:
            fps = None
        self.fps_override_value = fps

        self.video_format_value = self.video_format_var.get().upper()
        if self.video_format_value not in ("MP4", "GIF"):
            self.video_format_value = "MP4"

        self.two_pass_value = bool(self.two_pass_var.get())

        # Lock down controls
        self.is_running = True
        self.stop_flag.clear()
        self._set_controls_state("disabled")

        self.log("------------------------------------------------------------")
        self.log(
            f"Starting batch: {len(self.queue_items)} file(s), "
            f"target size ~ {target_mb} MB per file, "
            f"video format = {self.video_format_value}, "
            f"2-pass = {self.two_pass_value}"
        )

        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def stop_processing(self):
        if not self.is_running:
            return
        self.log("Stop requested. Waiting for current file to finish/abort...")
        self.stop_flag.set()

    def _set_controls_state(self, state):
        for widget in [
            self.btn_add_files,
            self.btn_remove_selected,
            self.btn_clear_queue,
            self.btn_start,
            self.entry_target_size,
            self.combo_video_format,
            self.entry_max_dim,
            self.entry_fps,
            self.chk_two_pass,
        ]:
            widget.config(state=state)

    # -------- WORKER THREAD --------

    def _worker_loop(self):
        total = len(self.queue_items)
        completed = 0
        failed = 0

        for idx, item in enumerate(self.queue_items):
            if self.stop_flag.is_set():
                item["status"] = "Cancelled"
                self._update_queue_list_in_ui_thread()
                break

            path = item["path"]
            info = item["info"]
            media_type = info["type"]

            item["status"] = "Processing"
            self._update_queue_list_in_ui_thread()
            self.log(f"Processing [{idx + 1}/{total}]: {path} ({media_type})")

            duration = info.get("duration", 0.0) or 0.0

            # Determine output path and encoding mode
            if media_type == "audio":
                # Always output MP3
                output_path = get_unique_output_path(path, "_compressed", ".mp3")

                def progress_cb(pct, t, line):
                    if pct is not None:
                        self.log(f"[AUDIO] {os.path.basename(path)} - {pct:.1f}% (time={t:.2f}s)")
                    elif line:
                        # occasional log of ffmpeg lines
                        if "error" in line.lower():
                            self.log(f"[AUDIO ffmpeg] {line}")

                rc = encode_audio_to_mp3(
                    input_path=path,
                    output_path=output_path,
                    target_bytes=self.target_bytes,
                    duration=duration,
                    progress_callback=progress_cb,
                    stop_flag=self.stop_flag
                )

            else:
                # video
                if self.video_format_value == "GIF":
                    output_ext = ".gif"
                else:
                    output_ext = ".mp4"

                output_path = get_unique_output_path(path, "_compressed", output_ext)

                def progress_cb(pct, t, line):
                    if pct is not None:
                        self.log(f"[VIDEO] {os.path.basename(path)} - {pct:.1f}% (time={t:.2f}s)")
                    elif line:
                        if "error" in line.lower():
                            self.log(f"[VIDEO ffmpeg] {line}")

                if self.video_format_value == "GIF":
                    rc = encode_video_to_gif(
                        input_path=path,
                        output_path=output_path,
                        target_bytes=self.target_bytes,
                        duration=duration,
                        src_info=info,
                        max_dim=self.max_dim_value,
                        fps_override=self.fps_override_value,
                        progress_callback=progress_cb,
                        stop_flag=self.stop_flag
                    )
                else:
                    rc = encode_video_to_mp4(
                        input_path=path,
                        output_path=output_path,
                        target_bytes=self.target_bytes,
                        duration=duration,
                        src_info=info,
                        max_dim=self.max_dim_value,
                        fps_override=self.fps_override_value,
                        two_pass=self.two_pass_value,
                        progress_callback=progress_cb,
                        stop_flag=self.stop_flag
                    )

            if rc == 0 and not self.stop_flag.is_set():
                completed += 1
                item["status"] = "Done"
                # Final stats
                src_size = os.path.getsize(path) if os.path.exists(path) else 0
                out_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
                self.log(
                    f"COMPLETED: {os.path.basename(path)} -> {os.path.basename(output_path)}\n"
                    f"  Source size:  {src_size} bytes\n"
                    f"  Output size:  {out_size} bytes\n"
                    f"  Saved to:     {output_path}"
                )
            else:
                if self.stop_flag.is_set():
                    item["status"] = "Cancelled"
                    self.log(f"Cancelled: {path}")
                else:
                    failed += 1
                    item["status"] = "Failed"
                    self.log(f"FAILED (rc={rc}): {path}")

            self._update_queue_list_in_ui_thread()

            if self.stop_flag.is_set():
                break

        # Summary
        left = sum(1 for i in self.queue_items if i["status"] == "Pending")
        self.log(
            f"Batch complete. "
            f"Total: {total}, Completed: {completed}, Failed: {failed}, "
            f"Pending: {left}."
        )

        # Clear queue after batch ends, regardless of success/failure
        self.queue_items = []
        self._update_queue_list_in_ui_thread()

        # Unlock controls
        self.is_running = False
        self.stop_flag.clear()
        self._set_controls_state("normal")

    def _update_queue_list_in_ui_thread(self):
        self.root.after(0, self._update_queue_listbox)


def main():
    root = tk.Tk()
    app = MediaCompressorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
