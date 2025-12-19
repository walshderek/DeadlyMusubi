import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from safetensors import safe_open
from safetensors.torch import save_file


class LoRAMetadataEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("LoRA Metadata Editor")
        self.file_path = None
        self.metadata = {}

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.setup_gui()

    def setup_gui(self):
        self.frame = ttk.Frame(self.root, padding="10")
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        self.select_button = ttk.Button(self.frame, text="Select .safetensors File", command=self.load_file)
        self.select_button.grid(row=0, column=0, sticky="ew", pady=5)

        self.entries_frame = ttk.LabelFrame(self.frame, text="Metadata")
        self.entries_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        self.entries_frame.columnconfigure(0, weight=1)
        self.entries_frame.rowconfigure(0, weight=1)

        self.entries_canvas = tk.Canvas(self.entries_frame)
        self.entries_scrollbar = ttk.Scrollbar(self.entries_frame, orient="vertical", command=self.entries_canvas.yview)
        self.entries_canvas.configure(yscrollcommand=self.entries_scrollbar.set)

        self.entries_canvas.grid(row=0, column=0, sticky="nsew")
        self.entries_scrollbar.grid(row=0, column=1, sticky="ns")

        self.entries_inner = ttk.Frame(self.entries_canvas)
        self.entries_inner.bind("<Configure>", lambda e: self.entries_canvas.configure(scrollregion=self.entries_canvas.bbox("all")))
        self.entries_canvas.create_window((0, 0), window=self.entries_inner, anchor="nw")

        self.entries_inner.columnconfigure(0, weight=0)
        self.entries_inner.columnconfigure(1, weight=1)

        self.save_button = ttk.Button(self.frame, text="Save Metadata", command=self.save_metadata)
        self.save_button.grid(row=2, column=0, sticky="ew", pady=5)

        self.entry_widgets = {}

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("SafeTensor files", "*.safetensors")])
        if not path:
            return

        self.file_path = path
        try:
            with safe_open(path, framework="pt", device="cpu") as f:
                self.metadata = f.metadata() or {}
                self.tensor_data = {key: f.get_tensor(key).detach().cpu() for key in f.keys()}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read metadata: {e}")
            return

        for widget in self.entries_inner.winfo_children():
            widget.destroy()

        self.entry_widgets.clear()
        for i, (key, value) in enumerate(self.metadata.items()):
            ttk.Label(self.entries_inner, text=key).grid(row=i, column=0, sticky="nw", padx=5, pady=2)

            if len(value) > 100 or '\n' in value:
                entry = tk.Text(self.entries_inner, height=3, wrap="word")
                entry.insert("1.0", value)
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
                self.entry_widgets[key] = (entry, True)
            else:
                entry = ttk.Entry(self.entries_inner, font=("Courier New", 10))
                entry.insert(0, value)
                entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
                self.entry_widgets[key] = (entry, False)

    def save_metadata(self):
        if not self.file_path:
            messagebox.showwarning("No File", "Please select a file first.")
            return

        try:
            for key, (widget, is_text) in self.entry_widgets.items():
                self.metadata[key] = widget.get("1.0", "end-1c") if is_text else widget.get()

            base_dir = os.path.dirname(self.file_path)
            file_name = os.path.basename(self.file_path)
            output_dir = os.path.join(base_dir, "edited metadata")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, file_name)

            save_file(self.tensor_data, output_path, metadata=self.metadata)
            messagebox.showinfo("Saved", f"Metadata written to:\n{output_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save metadata: {e}")


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("1200x800")
    app = LoRAMetadataEditor(root)
    root.mainloop()
