import os
import shutil
import re
from PIL import Image
from collections import defaultdict
from tkinter import filedialog, simpledialog, Tk
from datetime import datetime
import sys

ILLEGAL_CHARS = r'[<>:"/\\|?*]'
LORA_REGEX = re.compile(r"<lora:([^:>]+)(?::[^>]*)?>")


def sanitize(name):
    return re.sub(ILLEGAL_CHARS, "_", name)

def get_input_folder():
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    else:
        root = Tk()
        root.withdraw()
        folder = filedialog.askdirectory(title="Select Root Folder to Search")
    return folder

def get_search_term():
    root = Tk()
    root.withdraw()
    term = simpledialog.askstring("Search Term", "Enter the string to search for in LoRA names or prompts:")
    return term.strip() if term else None

def main():
    input_folder = get_input_folder()
    if not input_folder or not os.path.isdir(input_folder):
        print("❌ No valid folder selected.")
        return

    search_term = get_search_term()
    if not search_term:
        print("❌ No search term provided.")
        return

    search_term_lower = search_term.lower()
    target_folder_name = sanitize(search_term)
    target_folder = os.path.join(input_folder, target_folder_name)
    os.makedirs(target_folder, exist_ok=True)

    log_entries = []
    file_counters = defaultdict(int)
    log_path = os.path.join(input_folder, f"search_log_{target_folder_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

    for root_dir, _, files in os.walk(input_folder):
        for filename in files:
            if not filename.lower().endswith(".png"):
                continue

            image_path = os.path.join(root_dir, filename)

            try:
                with Image.open(image_path) as img:
                    metadata = img.info.get("parameters", "")
            except Exception as e:
                log_entries.append(f"❌ Failed to open {filename}: {e}")
                continue

            found = False
            if search_term_lower in metadata.lower():
                found = True
            else:
                lora_matches = LORA_REGEX.findall(metadata)
                if any(search_term_lower in lora.lower() for lora in lora_matches):
                    found = True

            if found:
                base_name, ext = os.path.splitext(filename)
                file_counters[filename] += 1
                new_name = f"{base_name}_{file_counters[filename]:03d}{ext}"
                dest_path = os.path.join(target_folder, new_name)
                try:
                    shutil.copy2(image_path, dest_path)
                    log_entries.append(f"✅ {filename} → {target_folder_name}/{new_name}")
                except Exception as e:
                    log_entries.append(f"❌ Failed to copy {filename} to {target_folder_name}: {e}")

    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write("\n".join(log_entries))

    print(f"✔️ Search complete. Log saved to:\n{log_path}")

if __name__ == "__main__":
    main()
