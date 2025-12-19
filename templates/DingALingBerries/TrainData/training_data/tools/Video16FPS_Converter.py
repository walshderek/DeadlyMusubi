
#!/usr/bin/env python3
# Video16FPS_Converter.py — Batch GUI to convert videos to constant 16 FPS for WAN 2.2 datasets.
# - GPU (NVENC) or CPU encoders, queue, live logs, per-file + overall progress.
# - Avoids CUDA hwframes/scaler requirements (compatible with vanilla ffmpeg builds).
# - Auto-mode prefers HEVC Main10 for >8‑bit sources, else H.264 NVENC.
#
# Requirements: ffmpeg + ffprobe on PATH (or pick via "Browse ffmpeg…").
# Windows: run with python 3.9+ (double-click if py assoc enabled).

import os
import re
import math
import json
import time
import shlex
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

VIDEO_EXTS = {".mp4",".mkv",".mov",".avi",".wmv",".flv",".webm",".mts",".m2ts",".m4v",".mpg",".mpeg"}

# ---------------------- FFPROBE HELPERS ----------------------

def run_json(cmd):
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return json.loads(p.stdout)
    except Exception:
        return None

def ffprobe_info(ffprobe_path, src):
    return run_json([ffprobe_path,"-v","error","-print_format","json","-show_streams","-show_format",src])

def get_video_stream_info(ffprobe_path, src):
    info = ffprobe_info(ffprobe_path, src)
    if not info: return {"duration": None, "bit_depth": 8, "pix_fmt": None}
    v = None
    for s in info.get("streams",[]):
        if s.get("codec_type") == "video":
            v = s; break
    if not v: return {"duration": None, "bit_depth": 8, "pix_fmt": None}

    # duration
    dur = None
    if "duration" in v:
        try: dur = float(v["duration"])
        except: pass
    if dur is None:
        try: dur = float(info.get("format",{}).get("duration"))
        except: dur = None

    pix_fmt = v.get("pix_fmt")
    bit_depth = 8
    if isinstance(pix_fmt, str):
        m = re.search(r"(\d+)", pix_fmt)
        if m:
            try: bit_depth = int(m.group(1))
            except: bit_depth = 8

    return {"duration": dur, "bit_depth": bit_depth, "pix_fmt": pix_fmt}

def fmt_hms(secs):
    if secs is None or math.isinf(secs) or math.isnan(secs): return "—"
    secs = max(0, int(secs))
    h = secs//3600; m=(secs%3600)//60; s=secs%60
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"

def list_videos(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for root,_,names in os.walk(p):
                for n in names:
                    if os.path.splitext(n)[1].lower() in VIDEO_EXTS:
                        files.append(os.path.join(root,n))
        else:
            if os.path.splitext(p)[1].lower() in VIDEO_EXTS:
                files.append(p)
    # dedupe keep order
    seen=set(); out=[]
    for f in files:
        if f not in seen:
            seen.add(f); out.append(f)
    return out

def detect_gpus():
    try:
        p = subprocess.run(["nvidia-smi","--query-gpu=name","--format=csv,noheader"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        names = [ln.strip() for ln in p.stdout.splitlines() if ln.strip()]
        return [(i, names[i]) for i in range(len(names))]
    except Exception:
        return []

def safe_out_path(in_path, out_dir, fps=16):
    base = os.path.basename(in_path)
    name, ext = os.path.splitext(base)
    if not ext: ext = ".mp4"
    return os.path.join(out_dir, f"{name}_{fps}FPS{ext}")

# ---------------------- COMMAND BUILDER ----------------------

class BuildCmdError(Exception): pass

class CmdBuilder:
    """
    Encoders:
      - "auto"         -> if bit_depth>8 and prefer_hevc10: HEVC (NVENC) profile main10; else H.264 (NVENC)
      - "h264_nvenc"   -> GPU H.264
      - "hevc_nvenc"   -> GPU HEVC (set profile main10 if user wants 10‑bit)
      - "libx264"      -> CPU H.264
      - "libx265"      -> CPU HEVC (uses 10‑bit if source is >8‑bit)
    Avoids CUDA hwframe filters; keeps pipeline broadly compatible.
    """
    def __init__(self, ffmpeg="ffmpeg", ffprobe="ffprobe", fps=16,
                 encoder="auto", prefer_hevc10=True,
                 use_hwdecode=True, gpu_index=0,
                 keep_audio=False, cq="19", preset="p5",
                 crf="18", x_preset="medium"):
        self.ffmpeg = ffmpeg
        self.ffprobe = ffprobe
        self.fps = int(fps)
        self.encoder = encoder
        self.prefer_hevc10 = prefer_hevc10
        self.use_hwdecode = use_hwdecode
        self.gpu_index = int(gpu_index)
        self.keep_audio = keep_audio
        # NVENC
        self.cq = str(cq)
        self.preset = str(preset)
        # CPU enc
        self.crf = str(crf)
        self.x_preset = str(x_preset)

    def build(self, src, dst, vinfo):
        bd = vinfo.get("bit_depth", 8) or 8
        enc = self.encoder

        if enc == "auto":
            if bd > 8 and self.prefer_hevc10:
                enc = "hevc_nvenc"
            else:
                enc = "h264_nvenc"

        cmd = [self.ffmpeg, "-hide_banner", "-y"]

        # Optional HW decode: use NVDEC without forcing CUDA hwframe output (no -hwaccel_output_format)
        if enc.endswith("_nvenc") and self.use_hwdecode:
            cmd += ["-hwaccel","cuda","-hwaccel_device",str(self.gpu_index)]

        cmd += ["-i", src, "-fps_mode","cfr","-r", str(self.fps)]

        # Audio mapping
        if self.keep_audio:
            cmd += ["-map","0:v:0","-map","0:a?","-c:a","aac","-b:a","192k"]
        else:
            cmd += ["-map","0:v:0","-an"]

        # Video encoder blocks (no pix_fmt forcing, no CUDA filters)
        if enc == "hevc_nvenc":
            cmd += ["-c:v","hevc_nvenc","-gpu",str(self.gpu_index),
                    "-preset",self.preset,
                    "-rc","vbr","-cq",self.cq,"-bf","2","-spatial_aq","1","-aq-strength","8",
                    "-movflags","+faststart"]
            # If user wants 10‑bit (auto or explicit): set profile main10 and let NVENC negotiate format.
            if bd > 8 and self.prefer_hevc10:
                cmd += ["-profile:v","main10"]
        elif enc == "h264_nvenc":
            cmd += ["-c:v","h264_nvenc","-gpu",str(self.gpu_index),
                    "-preset",self.preset,
                    "-rc","vbr","-cq",self.cq,"-bf","2","-spatial_aq","1","-aq-strength","8",
                    "-movflags","+faststart"]
        elif enc == "libx264":
            cmd += ["-c:v","libx264","-preset",self.x_preset,"-crf",self.crf,"-pix_fmt","yuv420p","-movflags","+faststart"]
        elif enc == "libx265":
            if bd > 8:
                cmd += ["-c:v","libx265","-preset",self.x_preset,"-crf",self.crf,"-pix_fmt","yuv420p10le","-movflags","+faststart"]
            else:
                cmd += ["-c:v","libx265","-preset",self.x_preset,"-crf",self.crf,"-pix_fmt","yuv420p","-movflags","+faststart"]
        else:
            raise BuildCmdError(f"Unsupported encoder: {enc}")

        cmd.append(dst)
        return cmd

# ---------------------- WORKER / PROGRESS ----------------------

TIME_RE = re.compile(r"time=(\d+):(\d+):(\d+)\.(\d+)")
def parse_timecode(line):
    m = TIME_RE.search(line)
    if not m: return None
    h, mnt, s, ms = m.groups()
    secs = int(h)*3600 + int(mnt)*60 + int(s) + (int(ms)/ (10**len(ms)))
    return secs

class Worker(threading.Thread):
    def __init__(self, files, out_dir, builder: CmdBuilder, ffprobe, log_fn, progress_fn, overall_fn, stop_flag):
        super().__init__(daemon=True)
        self.files = files
        self.out_dir = out_dir
        self.builder = builder
        self.ffprobe = ffprobe
        self.log = log_fn
        self.progress = progress_fn
        self.overall = overall_fn
        self.stop_flag = stop_flag

    def run(self):
        # Pre-compute durations for overall ETA
        total_secs = 0.0
        durations = {}
        for f in self.files:
            vi = get_video_stream_info(self.ffprobe, f)
            d = vi.get("duration") if vi else None
            durations[f] = d
            if d: total_secs += d

        done_secs = 0.0
        total_files = len(self.files)

        for idx, src in enumerate(self.files, 1):
            if self.stop_flag.is_set(): break

            vi = get_video_stream_info(self.ffprobe, src) or {}
            dur = vi.get("duration") or 0.0
            dst = safe_out_path(src, self.out_dir, self.builder.fps)
            self.log(f"\\n[{idx}/{total_files}] {src}\\n")
            try:
                cmd = self.builder.build(src, dst, vi)
            except BuildCmdError as e:
                self.log(f"Build error: {e}\\n")
                continue

            self.log(" ".join(shlex.quote(c) for c in cmd) + "\\n")

            start = time.time()
            last_tc = 0.0
            speeds = []
            N = 20

            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, universal_newlines=True)
            err_buf = []
            while True:
                if self.stop_flag.is_set():
                    try: proc.kill()
                    except: pass
                    return
                line = proc.stderr.readline()
                if not line:
                    if proc.poll() is not None: break
                    time.sleep(0.01); continue
                err_buf.append(line)
                tc = parse_timecode(line)
                if tc is not None and dur>0:
                    last_tc = max(last_tc, tc)
                    elapsed = time.time()-start
                    pct = min(100.0, (last_tc/dur)*100.0)
                    if elapsed>0:
                        sp = last_tc/elapsed
                        speeds.append(sp)
                        if len(speeds)>N: speeds.pop(0)
                        avg = sum(speeds)/len(speeds)
                        eta = (dur-last_tc)/avg if avg>0 else None
                    else:
                        eta = None
                    self.progress(idx, total_files, src, last_tc, dur, pct, eta, done_secs + last_tc)

            rc = proc.poll()
            if rc == 0:
                self.log("✓ Done.\\n")
                done_secs += dur or 0.0
            else:
                self.log("".join(err_buf) + "\\n")
                self.log(f"✗ FAILED (rc={rc}).\\n")

            # update overall bar
            if total_secs>0:
                pct = (done_secs/total_secs)*100.0
                self.overall(done_secs, total_secs, pct)
            else:
                pct = (idx/total_files)*100.0
                self.overall(idx, total_files, pct)

# ---------------------- GUI ----------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Convert to 16 FPS (GPU/CPU) — Queue + Log")
        self.geometry("1200x760")

        self.ffmpeg = "ffmpeg"
        self.ffprobe = "ffprobe"

        self.files = []
        self.out_dir = os.path.expanduser("~")

        # Options
        self.fps_var = tk.StringVar(value="16")
        self.encoder_var = tk.StringVar(value="auto")
        self.prefer_hevc10 = tk.BooleanVar(value=True)
        self.keep_audio = tk.BooleanVar(value=False)

        # GPU
        self.gpus = detect_gpus()
        self.gpu_idx_var = tk.StringVar(value="0")
        self.hwdecode_var = tk.BooleanVar(value=True)

        # Rate control
        self.cq_var = tk.StringVar(value="19")       # NVENC
        self.nv_preset_var = tk.StringVar(value="p5")
        self.crf_var = tk.StringVar(value="18")      # CPU
        self.x_preset_var = tk.StringVar(value="medium")

        self.stop_flag = threading.Event()

        self._build_ui()
        self._log("Ready.\\n")

    def _build_ui(self):
        main = ttk.Frame(self); main.grid(row=0, column=0, sticky="nsew"); 
        self.grid_rowconfigure(0, weight=1); self.grid_columnconfigure(0, weight=1)

        # Top controls
        top = ttk.Frame(main); top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=8, pady=6)
        ttk.Button(top, text="Add Files", command=self.add_files).grid(row=0, column=0, padx=4)
        ttk.Button(top, text="Add Folder", command=self.add_folder).grid(row=0, column=1, padx=4)
        ttk.Button(top, text="Remove Selected", command=self.remove_selected).grid(row=0, column=2, padx=4)
        ttk.Button(top, text="Clear Queue", command=self.clear_files).grid(row=0, column=3, padx=4)
        ttk.Button(top, text="Choose Output Folder", command=self.choose_out).grid(row=0, column=4, padx=4)
        self.out_lbl = ttk.Label(top, text=self.out_dir, width=60); self.out_lbl.grid(row=0, column=5, sticky="w")

        # Left: queue
        left = ttk.LabelFrame(main, text="Queue"); left.grid(row=1, column=0, sticky="nsew", padx=8, pady=6)
        self.listbox = tk.Listbox(left, height=18, selectmode="extended")
        self.listbox.grid(row=0, column=0, sticky="nsew")
        left.grid_rowconfigure(0, weight=1); left.grid_columnconfigure(0, weight=1)

        # Right: log
        right = ttk.LabelFrame(main, text="Log"); right.grid(row=1, column=1, sticky="nsew", padx=8, pady=6)
        self.logbox = tk.Text(right, height=18, wrap="word")
        self.logbox.grid(row=0, column=0, sticky="nsew")
        right.grid_rowconfigure(0, weight=1); right.grid_columnconfigure(0, weight=1)

        # Options
        opts = ttk.LabelFrame(main, text="Options"); opts.grid(row=2, column=0, columnspan=2, sticky="ew", padx=8, pady=6)

        c = 0
        ttk.Label(opts, text="FPS:").grid(row=0, column=c, sticky="e"); c+=1
        ttk.Entry(opts, textvariable=self.fps_var, width=6).grid(row=0, column=c, sticky="w", padx=6); c+=1

        ttk.Label(opts, text="Encoder:").grid(row=0, column=c, sticky="e"); c+=1
        enc = ttk.Combobox(opts, textvariable=self.encoder_var, state="readonly",
                           values=["auto","h264_nvenc","hevc_nvenc","libx264","libx265"], width=12)
        enc.grid(row=0, column=c, sticky="w", padx=6); c+=1

        ttk.Checkbutton(opts, text="Prefer HEVC Main10 for >8-bit (Auto)", variable=self.prefer_hevc10).grid(row=0, column=c, sticky="w", padx=12); c+=1
        ttk.Checkbutton(opts, text="Keep Audio", variable=self.keep_audio).grid(row=0, column=c, sticky="w", padx=12); c+=1

        # NVENC
        row1 = 1; c = 0
        ttk.Checkbutton(opts, text="HW Decode (CUDA)", variable=self.hwdecode_var).grid(row=row1, column=c, sticky="w", padx=6); c+=1

        ttk.Label(opts, text="GPU:").grid(row=row1, column=c, sticky="e"); c+=1
        if self.gpus:
            display=[f"{i}: {n}" for i,n in self.gpus]
            self.gpu_combo = ttk.Combobox(opts, values=display, state="readonly", width=40)
            self.gpu_combo.grid(row=row1, column=c, sticky="w", padx=6)
            self.gpu_combo.current(0)
        else:
            self.gpu_idx_entry = ttk.Entry(opts, textvariable=self.gpu_idx_var, width=6)
            self.gpu_idx_entry.grid(row=row1, column=c, sticky="w", padx=6)
            ttk.Label(opts, text="(GPU index)").grid(row=row1, column=c+1, sticky="w")
        c+=1

        ttk.Label(opts, text="NVENC Preset:").grid(row=row1, column=c, sticky="e"); c+=1
        ttk.Combobox(opts, textvariable=self.nv_preset_var, state="readonly",
                     values=["p1","p2","p3","p4","p5","p6","p7"], width=6).grid(row=row1, column=c, sticky="w", padx=6); c+=1

        ttk.Label(opts, text="NVENC CQ:").grid(row=row1, column=c, sticky="e"); c+=1
        ttk.Entry(opts, textvariable=self.cq_var, width=6).grid(row=row1, column=c, sticky="w", padx=6); c+=1

        # CPU
        row2 = 2; c = 0
        ttk.Label(opts, text="CPU CRF:").grid(row=row2, column=c, sticky="e"); c+=1
        ttk.Entry(opts, textvariable=self.crf_var, width=6).grid(row=row2, column=c, sticky="w", padx=6); c+=1
        ttk.Label(opts, text="CPU Preset:").grid(row=row2, column=c, sticky="e"); c+=1
        ttk.Combobox(opts, textvariable=self.x_preset_var, state="readonly",
                     values=["ultrafast","superfast","veryfast","faster","fast","medium","slow","slower","veryslow"], width=10)\
            .grid(row=row2, column=c, sticky="w", padx=6); c+=1

        # Progress
        prog = ttk.Frame(main); prog.grid(row=3, column=0, columnspan=2, sticky="ew", padx=8, pady=6)
        self.file_prog = ttk.Progressbar(prog, maximum=100.0); self.file_prog.grid(row=0, column=0, columnspan=2, sticky="ew", pady=2)
        self.all_prog  = ttk.Progressbar(prog, maximum=100.0); self.all_prog.grid(row=1, column=0, columnspan=2, sticky="ew", pady=2)
        self.status = ttk.Label(prog, text="—"); self.status.grid(row=2, column=0, columnspan=2, sticky="w")

        # Buttons
        btns = ttk.Frame(main); btns.grid(row=4, column=0, columnspan=2, sticky="ew", padx=8, pady=8)
        ttk.Button(btns, text="Browse ffmpeg…", command=self.browse_ffmpeg).grid(row=0, column=0, padx=4)
        self.start_btn = ttk.Button(btns, text="Start", command=self.start); self.start_btn.grid(row=0, column=1, padx=6)
        self.stop_btn  = ttk.Button(btns, text="Stop", command=self.stop, state="disabled"); self.stop_btn.grid(row=0, column=2, padx=6)

        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)

    # ---------- UI actions ----------

    def add_files(self):
        paths = filedialog.askopenfilenames(title="Select Videos")
        if not paths: return
        self.files += list_videos(paths)
        self._refresh_queue()

    def add_folder(self):
        p = filedialog.askdirectory(title="Select Folder")
        if not p: return
        self.files += list_videos([p])
        self._refresh_queue()

    def remove_selected(self):
        sels = list(self.listbox.curselection())
        if not sels: return
        sels.reverse()
        for i in sels:
            try: self.files.pop(i)
            except: pass
        self._refresh_queue()

    def clear_files(self):
        self.files = []; self._refresh_queue()

    def choose_out(self):
        p = filedialog.askdirectory(title="Select Output Folder", initialdir=self.out_dir)
        if p:
            self.out_dir = p
            self.out_lbl.config(text=p)

    def browse_ffmpeg(self):
        p = filedialog.askopenfilename(title="Select ffmpeg executable",
                                       filetypes=[("ffmpeg", "ffmpeg ffmpeg.exe"), ("All files", "*.*")])
        if p:
            self.ffmpeg = p
            folder = os.path.dirname(p)
            cand = os.path.join(folder, "ffprobe.exe" if os.name=="nt" else "ffprobe")
            self.ffprobe = cand if os.path.exists(cand) else "ffprobe"
            messagebox.showinfo("ffmpeg selected", f"ffmpeg: {self.ffmpeg}\nffprobe: {self.ffprobe}")

    def _refresh_queue(self):
        self.listbox.delete(0,"end")
        for f in self.files:
            self.listbox.insert("end", f)

    def _log(self, msg):
        self.logbox.insert("end", msg)
        self.logbox.see("end")
        self.update_idletasks()

    def _progress(self, idx, total, src, tc, dur, pct, eta, overall_secs_done):
        self.file_prog["value"] = pct
        left = fmt_hms(eta) if eta is not None else "—"
        self.status.config(text=f"[{idx}/{total}] {os.path.basename(src)}  |  {tc:.1f}/{dur:.1f}s  |  {pct:.1f}%  |  ETA {left}")
        self.update_idletasks()

    def _overall(self, done, total, pct):
        self.all_prog["value"] = pct
        self.update_idletasks()

    def start(self):
        if not self.files:
            messagebox.showwarning("No files","Add at least one video.")
            return
        try:
            fps = int(round(float(self.fps_var.get())))
            if fps <= 0: raise ValueError
        except:
            messagebox.showerror("FPS","Enter a positive FPS (e.g., 16)."); return

        # GPU index from combo or entry
        if hasattr(self, "gpu_combo") and isinstance(self.gpu_combo, ttk.Combobox) and self.gpu_combo.get():
            sel = self.gpu_combo.get().split(":")[0].strip()
            try: gpu_idx = int(sel)
            except: gpu_idx = 0
        else:
            try: gpu_idx = int(self.gpu_idx_var.get())
            except: gpu_idx = 0

        builder = CmdBuilder(
            ffmpeg=self.ffmpeg, ffprobe=self.ffprobe, fps=fps,
            encoder=self.encoder_var.get(),
            prefer_hevc10=self.prefer_hevc10.get(),
            use_hwdecode=self.hwdecode_var.get(),
            gpu_index=gpu_idx,
            keep_audio=self.keep_audio.get(),
            cq=self.cq_var.get(), preset=self.nv_preset_var.get(),
            crf=self.crf_var.get(), x_preset=self.x_preset_var.get()
        )

        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.stop_flag = threading.Event()
        self._log("\\nStarting…\\n")

        self.worker = Worker(self.files, self.out_dir, builder, self.ffprobe, self._log, self._progress, self._overall, self.stop_flag)
        self.worker.start()

    def stop(self):
        if hasattr(self, "worker"):
            self.stop_flag.set()
            self._log("\\nStopping…\\n")

    def run(self):
        self.mainloop()

if __name__ == "__main__":
    App().run()
