import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
import os
from functools import partial

from utils_v2 import iterate_root_folder, process_file


class GallerySorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gallery Date Sorter")
        self.root.geometry("400x200")

        # Select folder label and button
        self.label = tk.Label(root, text="Select a folder to sort:")
        self.label.pack(pady=10)

        self.folder_path_var = tk.StringVar()
        self.folder_entry = tk.Entry(root, textvariable=self.folder_path_var, width=50)
        self.folder_entry.pack(pady=5)

        self.browse_button = tk.Button(root, text="Browse", command=self.browse_folder)
        self.browse_button.pack(pady=5)

        # Sort button
        self.sort_button = tk.Button(root, text="Sort Files", command=self.start_sorting)
        self.sort_button.pack(pady=20)

        # Status label
        self.status_label = tk.Label(root, text="")
        self.status_label.pack(pady=10)

    def browse_folder(self):
        """Open a dialog to select a folder."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path_var.set(folder_selected)

    def start_sorting(self):
        """Start the sorting process in a separate thread."""
        folder_path = self.folder_path_var.get()
        if not folder_path or not os.path.exists(folder_path):
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        # Disable the sort button to prevent multiple clicks
        self.sort_button.config(state=tk.DISABLED)
        self.status_label.config(text="Sorting in progress...")

        # Start sorting in a new thread to keep the GUI responsive
        thread = Thread(target=self.sort_files, args=(folder_path,))
        thread.start()

    def sort_files(self, folder_path):
        """Sort the files and update the UI once done."""
        try:
            process_file_partial = partial(process_file, destination_folder=folder_path)
            iterate_root_folder(folder_path, process_file_partial)
            self.status_label.config(text="Sorting completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_label.config(text="Sorting failed.")
        finally:
            # Re-enable the sort button after completion
            self.sort_button.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = GallerySorterApp(root)
    root.mainloop()
