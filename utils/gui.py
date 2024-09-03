import os.path
import time

import customtkinter as tk
from CTkMessagebox import CTkMessagebox
from functools import partial
from utils import iterate_root_folder, process_file, get_number_of_processable_files

class GallerySorterGUI:

    def __init__(self):

        self.progress_bar_step = None

        # Create GUI
        self.root = tk.CTk()
        self.root.geometry("800x500")
        self.root.title("Gallery sorter")

        # FOLDER INPUT
        self.folder_input_label = tk.CTkLabel(self.root, text="Folder to process:", font=("Arial", 16))
        self.folder_input_label.pack(padx=15, pady=8)

        self.folder_input = tk.CTkTextbox(self.root, font=("Arial", 16), height=30)
        self.folder_input.pack(padx=10)

        # PROGRESS BAR
        self.progress_bar_label = tk.CTkLabel(self.root, text="Progress:", font=("Arial", 16))
        self.progress_bar = tk.CTkProgressBar(self.root, mode="determinate")
        self.progress_bar.place(relx=0.5, rely=0.6, anchor="center")
        self.progress_bar.set(0)

        # IGNORE DUPLICATES
        self.dont_move_if_exists_checkbox_state = tk.IntVar()
        self.dont_move_if_exists_checkbox = tk.CTkCheckBox(self.root,
                                                         text="Don't move if file exists",
                                                         font=("Arial", 16),
                                                         variable=self.dont_move_if_exists_checkbox_state)
        self.dont_move_if_exists_checkbox.pack(padx=10, pady=10)

        # START BUTTON
        self.start_button = tk.CTkButton(self.root, text="Start", font=("Arial", 16), command=self.start_function)
        self.start_button.pack(padx=10, pady=10)

        # RUN
        self.root.mainloop()

    def progress_process_file(self, root_folder, file_path, dont_move_if_exists=False):
        result = process_file(root_folder, file_path, dont_move_if_exists=dont_move_if_exists)
        self.progress_bar.set(self.progress_bar.get() + self.progress_bar_step)
        return result

    def start_function(self):

        folder = self.folder_input.get("1.0", "end-1c")

        if not os.path.exists(folder):
            CTkMessagebox(title="Error", message=f"Folder {folder} does not exist", icon="cancel")
        else:
            total_files = get_number_of_processable_files(folder)
            self.progress_bar_step = 1/total_files
            part_process_file = partial(self.progress_process_file,
                                        dont_move_if_exists=self.dont_move_if_exists_checkbox_state)

            iterate_root_folder(folder, part_process_file)



if __name__ == "__main__":
    gui = GallerySorterGUI()
