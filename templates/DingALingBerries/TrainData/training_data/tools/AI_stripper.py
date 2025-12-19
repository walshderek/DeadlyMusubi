import os
import subprocess
import imageio.v3 as iio
from PIL import Image
from tkinter import Tk, filedialog

# Suppress tkinter window
Tk().withdraw()

# Prompt for folder
source_folder = filedialog.askdirectory(title="Select Folder Containing Files")
if not source_folder:
    print("No folder selected. Exiting.")
    exit()

output_folder = os.path.join(source_folder, "stripped")
os.makedirs(output_folder, exist_ok=True)

# Strip metadata from PNG
def strip_png(input_path, output_path):
    try:
        img = Image.open(input_path)
        img.save(output_path, format="PNG")
        print(f"[PNG] Stripped: {output_path}")
    except Exception as e:
        print(f"[PNG] Failed: {e}")

# Strip metadata from animated WebP
def strip_webp(input_path, output_path):
    try:
        frames = list(iio.imiter(input_path))
        iio.imwrite(output_path, frames, plugin="pillow", format="WEBP", loop=0)
        print(f"[WEBP] Stripped: {output_path}")
    except Exception as e:
        print(f"[WEBP] Failed: {e}")

# Strip metadata from MP4 using ffmpeg
def strip_mp4(input_path, output_path):
    try:
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-map_metadata", "-1",
            "-c:v", "copy", "-c:a", "copy",
            output_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[MP4] Stripped: {output_path}")
    except Exception as e:
        print(f"[MP4] Failed: {e}")

# File loop
for root, _, files in os.walk(source_folder):
    for file in files:
        src = os.path.join(root, file)
        rel_path = os.path.relpath(src, source_folder)
        dest = os.path.join(output_folder, rel_path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        ext = os.path.splitext(file)[1].lower()
        if ext == ".png":
            strip_png(src, dest)
        elif ext == ".webp":
            strip_webp(src, dest)
        elif ext == ".mp4":
            strip_mp4(src, dest)
