# Gallery Date Sorter

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

# TODO: 
    - Add support for HEIC images: Try exiftool or exifreader instead of ffmpeg for exif data reading.
    - Add executable download.

## Overview

Gallery Date Sorter is a Python-based utility designed to help you organize your images and videos into neatly structured folders based on their creation dates. The application sorts files into `YYYY-MM` format folders, simplifying the organization of large collections of media files.

The tool comes with a simple and intuitive GUI that allows you to easily select the source folder, configure your sorting options, and monitor the progress of the sorting process.

## Features

- **Image and Video Sorting**: Automatically organize your files into folders based on their creation dates.
- **Customizable Options**:
  - **Copy or Move**: Choose whether to copy or move files during the sorting process.
  - **Skip Existing Files**: Option to skip moving files if they already exist in the destination folder.
  - **Custom Output Folder**: Specify a different folder for the sorted files.
- **Progress Tracking**: A visual progress bar to track the sorting process.
- **Multi-Platform Support**: Compatible with Windows, macOS, and Linux.

## Installation

### Prerequisites

- Python 3.8 or higher
- `pip` (Python package manager)

### Step-by-Step Guide

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/gallery-date-sorter.git
   cd gallery-date-sorter
   ```

2. **Install Required Dependencies**:
   Install the necessary Python packages using the following command:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

To start the application, run the following command:

```bash
python main.py
```

This will launch the GUI, where you can select the folder to sort, configure your options, and start sorting.

## Usage

### GUI Walkthrough

1. **Select Folder**: Use the "Browse" button to select the folder containing your images and videos.
2. **(Optional) Select Output Folder**: Choose a different output folder if you don't want to sort the files within the source folder.
3. **Configure Options**:
   - **Copy Files Instead of Moving**: Toggle this option if you want to keep the original files in place and copy them to the sorted folders.
   - **Don't Move If File Already Exists**: Prevents files from being moved if they already exist in the destination.
4. **Start Sorting**: Click "Sort Files" to begin the sorting process. You can monitor the progress via the progress bar.

### Command-Line Usage

For advanced users, the sorting logic can also be accessed programmatically via the `utils` module. This allows for integration into scripts or other applications.

## Contributing

Contributions are welcome! Whether it's fixing bugs, adding new features, or improving the documentation, your help is appreciated.

1. **Fork the Repository**: Create a fork of the project on GitHub.
2. **Create a Branch**: Create a new branch for your feature or bugfix.
   ```bash
   git checkout -b feature/my-feature
   ```
3. **Submit a Pull Request**: After making your changes, submit a pull request to the `main` branch.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

- [PIL](https://pillow.readthedocs.io/) for image processing.
- [FFmpeg](https://ffmpeg.org/) for handling video metadata.
- [Tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI framework.

---
