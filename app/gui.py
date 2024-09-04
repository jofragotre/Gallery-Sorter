import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from threading import Thread
import os
from utils import iterate_root_folder, process_file


class GallerySorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gallery Date Sorter")
        self.root.geometry("500x500")

        # Folder selection
        self.label = tk.Label(root, text="Select a folder to sort:")
        self.label.pack(pady=10)

        self.source_folder_var = tk.StringVar()
        self.folder_entry = tk.Entry(root, textvariable=self.source_folder_var, width=60)
        self.folder_entry.pack(pady=5)

        self.browse_button = tk.Button(root, text="Browse", command=self.browse_source_folder)
        self.browse_button.pack(pady=5)

        # Output folder selection (optional)
        self.output_label = tk.Label(root, text="Select an output folder (optional):")
        self.output_label.pack(pady=10)

        self.destination_folder_var = tk.StringVar()
        self.output_entry = tk.Entry(root, textvariable=self.destination_folder_var, width=60)
        self.output_entry.pack(pady=5)

        self.output_browse_button = tk.Button(root, text="Browse", command=self.browse_destination_folder)
        self.output_browse_button.pack(pady=5)

        # Options for copying or moving files
        self.copy_move_var = tk.BooleanVar(value=False)
        self.copy_move_check = tk.Checkbutton(root, text="Copy files instead of moving", variable=self.copy_move_var)
        self.copy_move_check.pack(pady=5)

        # Option to skip moving if file exists
        self.dont_move_if_exists_var = tk.BooleanVar(value=False)
        self.dont_move_if_exists_check = tk.Checkbutton(root, text="Don't move if file already exists",
                                                        variable=self.dont_move_if_exists_var)
        self.dont_move_if_exists_check.pack(pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=20)

        # Sort button
        self.sort_button = tk.Button(root, text="Sort Files", command=self.start_sorting)
        self.sort_button.pack(pady=20)

        # Status label
        self.status_label = tk.Label(root, text="")
        self.status_label.pack(pady=10)

    def browse_source_folder(self):
        """Open a dialog to select a folder."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.source_folder_var.set(folder_selected)

    def browse_destination_folder(self):
        """Open a dialog to select an output folder."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.destination_folder_var.set(folder_selected)

    def start_sorting(self):
        """Start the sorting process in a separate thread."""
        source_folder = self.source_folder_var.get()
        destination_folder = self.destination_folder_var.get() or source_folder

        if not source_folder or not os.path.exists(source_folder):
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        # Disable the sort button to prevent multiple clicks
        self.sort_button.config(state=tk.DISABLED)
        self.status_label.config(text="Sorting in progress...")
        self.progress['value'] = 0

        # Start sorting in a new thread to keep the GUI responsive
        thread = Thread(target=self.sort_files, args=(source_folder, destination_folder))
        thread.start()

    def sort_files(self, source_folder, destination_folder):
        """Sort the files and update the UI once done."""
        try:
            file_count = len([file for _, _, files in os.walk(source_folder) for file in files])
            self.progress['maximum'] = file_count

            def wrapped_process_file(file_path, destination_folder_=destination_folder):
                process_file(destination_folder=destination_folder_,
                             file_path=file_path,
                             dont_move_if_exists=self.dont_move_if_exists_var.get(),
                             copy=self.copy_move_var.get(),)
                self.progress.step(1)
                self.root.update_idletasks()

            iterate_root_folder(source_folder, wrapped_process_file)
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
