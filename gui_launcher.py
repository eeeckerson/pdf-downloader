import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import subprocess
import threading
import sys

def run_script():
    gui_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(gui_dir, "pdf_downloader.py")
    input_dir = os.path.join(gui_dir, "input")
    gui_log_path = os.path.join(gui_dir, "logs", "gui_log.txt")
    os.makedirs(os.path.join(gui_dir, "logs"), exist_ok=True)

    required_files = [
        os.path.join(input_dir, "base-url.csv"),
        os.path.join(input_dir, "sec-grp-url.csv"),
        os.path.join(input_dir, "year-url.csv")
    ]

    if not os.path.exists(script_path):
        msg = f"Cannot find pdf_downloader.py at {script_path}"
        messagebox.showerror("Error", msg)
        with open(gui_log_path, "a") as gl:
            gl.write(msg + "\n")
        return

    if not all(os.path.isfile(f) for f in required_files):
        msg = "One or more required input CSV files are missing in the 'input' folder."
        messagebox.showerror("Error", msg)
        with open(gui_log_path, "a") as gl:
            gl.write(msg + "\n")
        return

    progress_bar.start()
    status_label.config(text="Processing...")

    def background_task():
        try:
            subprocess.run([sys.executable, script_path], check=True)
            status_label.config(text="✅ Done. Check folders for results.")
            messagebox.showinfo("Done", "PDF download complete! Check your folders.")
        except subprocess.CalledProcessError as e:
            status_label.config(text="❌ Script failed.")
            messagebox.showerror("Error", "Script failed. Check logs for details.")
            with open(gui_log_path, "a") as gl:
                gl.write(f"Script failed with error: {e}\n")
        finally:
            progress_bar.stop()

    threading.Thread(target=background_task).start()

root = tk.Tk()
root.title("PDF Downloader (Auto Input with Progress Bar)")

tk.Label(root, text="Input files will be read automatically from the 'input/' folder.").grid(row=0, column=0, columnspan=2, pady=(10, 5))
tk.Label(
    root,
    text="- base-url.csv\n- sec-grp-url.csv\n- year-url.csv (inside 'input/' folder)",
    justify="left"
).grid(row=1, column=0, columnspan=2, pady=5)

tk.Button(root, text="Start Import", command=run_script, bg="green", fg="white").grid(row=2, column=0, columnspan=2, pady=10)

progress_bar = ttk.Progressbar(root, mode='indeterminate', length=280)
progress_bar.grid(row=3, column=0, columnspan=2, pady=5)

status_label = tk.Label(root, text="Idle")
status_label.grid(row=4, column=0, columnspan=2, pady=(0, 10))

root.mainloop()
