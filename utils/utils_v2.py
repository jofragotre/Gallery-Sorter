"""
Gallery date sorter utils

"""

import os
import time
from logging import Logger
import datetime
import logging
import ffmpeg
import shutil
from tqdm import tqdm
from PIL import Image, ExifTags, UnidentifiedImageError
from pathlib import Path
from pillow_heif import register_heif_opener
from functools import partial


# Register heif for HEIC type images
register_heif_opener()

# Define logger
sorter_logger: Logger = logging.getLogger('image_video_sorter')
sorter_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
sorter_logger.addHandler(handler)

# Define image and video extensions
IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "ppm", "tif", "tiff", "bmp", "heic"}
VIDEO_EXTENSIONS = {"mov", "mp4", "avi"}

# Define date tags
DATE_TAGS = {
    ExifTags.TAGS[k]: k for k in ExifTags.TAGS.keys() if ExifTags.TAGS[k] in {
        'DateTimeOriginal', 'DateTime', 'DateTimeDigitized', 'PreviewDateTime'
    }
}


def get_file_modification_date(file_path):
    """Get the last modification date of a file as a fallback."""
    m_time = os.path.getmtime(file_path)
    return datetime.datetime.fromtimestamp(m_time).strftime("%Y:%m:%d %H:%M:%S")


def get_image_creation_date(image_path):
    """Get image creation date from image metadata."""
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if exif_data is not None:
            for date_tag in DATE_TAGS.values():
                tag_value = exif_data.get(date_tag)
                if tag_value:
                    return tag_value
    except UnidentifiedImageError:
        sorter_logger.error(f"Error opening image: {image_path}")
    except OSError as e:
        sorter_logger.error(f"Error reading EXIF data from image {image_path}: {e}")
    except AttributeError as e:
        sorter_logger.error(f"Error reading EXIF data from image {image_path}: {e}")

    return get_file_modification_date(image_path)


def get_video_creation_date(video_path):
    """Get the creation date of a video file."""
    try:
        metadata = ffmpeg.probe(video_path)
        if 'format' in metadata and 'tags' in metadata['format']:
            creation_date = metadata['format']['tags'].get('creation_time')
            if creation_date:
                return creation_date
    except ffmpeg.Error as e:
        sorter_logger.error(f"Error reading metadata from video {video_path}: {e}")

    return get_file_modification_date(video_path)


def get_number_of_processable_files(root_folder):
    """Get the number of processable files in the root folder."""
    count = 0
    for root, _, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith(tuple(IMAGE_EXTENSIONS | VIDEO_EXTENSIONS)):
                count += 1
    return count


def iterate_root_folder(root_folder, function):
    """Iterate through the root folder and process each file."""
    paths = []
    for root, _, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith(tuple(IMAGE_EXTENSIONS | VIDEO_EXTENSIONS)):
                paths.append(Path(root) / file)

    pbar = tqdm(paths)
    for file_path in pbar:
        result = (function(file_path=file_path))
        pbar.set_description(result)


def create_date_folder(root_folder, date):
    """Create a folder with the given date in the specified root folder."""
    date_folder = Path(root_folder) / date
    date_folder.mkdir(parents=True, exist_ok=True)
    return date_folder


def check_if_on_correct_folder(root_folder, file_path, creation_date):
    """Check if the file is in the correct folder based on the creation date."""
    try:
        date_folder = Path(file_path).relative_to(root_folder).parts[0]
        return date_folder == creation_date
    except ValueError:
        return False

def copy_file_to_folder(file_path, date_folder):
    """Copy a file to a specified folder."""
    file_path = Path(file_path)
    target_path = date_folder / file_path.name
    if target_path.exists():
        return None
    shutil.copy(str(file_path), str(target_path))
    return target_path


def move_file_to_folder(file_path, date_folder, dont_move_if_exists=False):
    """Move a file to a specified folder."""
    file_path = Path(file_path)
    target_path = date_folder / file_path.name

    if dont_move_if_exists and target_path.exists():
        return None

    while target_path.exists():
        target_path = target_path.with_name(f"{target_path.stem}_copy{target_path.suffix}")

    file_path.rename(target_path)
    return target_path


def process_file(destination_folder, file_path: Path, dont_move_if_exists=False, copy=False):
    """Process a file based on its type and creation date."""

    if str(file_path).lower().endswith(tuple(IMAGE_EXTENSIONS)):
        creation_date = get_image_creation_date(file_path)
    elif str(file_path).lower().endswith(tuple(VIDEO_EXTENSIONS)):
        creation_date = get_video_creation_date(file_path)
    else:
        return None

    if creation_date is None:
        destiny_folder = create_date_folder(destination_folder, "Unsorted")
    else:
        creation_date_yyyy_mm = f"{creation_date[:4]}-{creation_date[5:7]}"
        folder_check = check_if_on_correct_folder(destination_folder, file_path, creation_date_yyyy_mm)
        if not folder_check:
            destiny_folder = create_date_folder(destination_folder, creation_date_yyyy_mm)
        else:
            return_string = f"File {file_path} already in correct folder"
            sorter_logger.debug(return_string)
            return return_string

    if not copy:
        # Move the file to the correct folder
        new_path = move_file_to_folder(file_path, destiny_folder, dont_move_if_exists)
        if new_path is not None:
            return_string = f"Moved {file_path} to {new_path}"
        sorter_logger.debug(return_string)
    else:
        # Copy the file to the correct folder
        new_path = copy_file_to_folder(file_path, destiny_folder)
        if new_path is not None:
            return_string = f"Copied {file_path} to {new_path}"
        else:
            return_string = f"File {file_path} already exists in {destiny_folder}"
        sorter_logger.debug(return_string)

    return return_string

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sort images and videos by creation date.")
    parser.add_argument("-src", "--source", help="Source folder to process", required=True)
    parser.add_argument("-dst", "--destination", help="Destination folder, if omitted source folder will be used", required=False)
    parser.add_argument("-c", "--copy", help="Copy files instead of moving them", action="store_true")
    parser.add_argument("-nc", "--no_copy", help="Do not copy files instead of moving them", dest="copy", action="store_false")
    parser.set_defaults(copy=False)
    args = parser.parse_args()

    # Set destination folder to source folder if not specified
    if args.destination is None:
        args.destination = args.source
    else:
        print(f"Destination folder: {args.destination}")

    process_file_partial = partial(process_file, destination_folder=args.destination, copy=args.copy)

    iterate_root_folder(args.source, process_file_partial)
