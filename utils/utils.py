"""
Gallery date sorter utils

"""

import os
import time
from logging import Logger
import datetime
import logging
import ffmpeg
from tqdm import tqdm
import PIL
from PIL import Image
from PIL.ExifTags import TAGS

# Define logger
sorter_logger: Logger = logging.getLogger('image_video_sorter')

# Define image and video extensions
IMAGE_EXTENSIONS = ["jpg", "JPG", "png", "PNG", "ppm", "PPM",
                    "tif", "TIF", "tiff", "TIFF", "bmp", "BMP",
                    "JPEG", "jpeg", "heic", "HEIC"]

VIDEO_EXTENSIONS = ["mov", "MOV", "mp4", "MP4", "avi", "AVI"]

# Define date tags
date_tags = ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized', 'PreviewDateTime']
DATE_TAGS = []
for tag_number, tag in TAGS.items():
    if tag in date_tags:
        DATE_TAGS.append(tag_number)


def get_image_creation_date(image_path):
    """
    Get image creation date from image metadata.

    :param image_path: Absolute path to the image.
    :return: Creation date of the image in format YYYY:MM:DD HH:MM:SS.
    """

    try:
        img = Image.open(image_path)

        try:
            exif_data = img._getexif()

        except OSError:
            sorter_logger.log("Error reading EXIF data from image")
            exif_data = None

        if exif_data is not None:
            for date_tag in DATE_TAGS:
                tag_value = exif_data.get(date_tag)
                if tag_value:
                    return tag_value

    except PIL.UnidentifiedImageError:
        sorter_logger.log("Error opening image")

    ti_m = os.path.getmtime(image_path)
    # Converting the time in seconds to a timestamp
    m_ti = time.ctime(ti_m)
    # Parse the input date string to a datetime object
    date_object = datetime.datetime.strptime(m_ti, "%a %b %d %H:%M:%S %Y")

    # Format the datetime object into the desired format
    m_ti = date_object.strftime("%Y:%m:%d %H:%M:%S")
    return m_ti


def get_video_creation_date(video_path):
    """
    Get the creation date of a video file.
    Args:
        video_path (str): The path to the video file.
    Returns:
        str: The creation date of the video file in the format "YYYY:MM:DD HH:MM:SS".
            If the creation date cannot be found in the video metadata, the function
            returns the creation time of the video file in the same format.
    Raises:
        None.
    """

    metadata = ffmpeg.probe(video_path)

    if 'format' in metadata and 'tags' in metadata['format']:
        creation_date = metadata['format']['tags'].get('creation_time')

        if creation_date:
            return creation_date

        ti_m = os.path.getmtime(video_path)
        # Converting the time in seconds to a timestamp
        m_ti = time.ctime(ti_m)
        # Parse the input date string to a datetime object
        date_object = datetime.datetime.strptime(m_ti, "%a %b %d %H:%M:%S %Y")
        # Format the datetime object into the desired format
        m_ti = date_object.strftime("%Y:%m:%d %H:%M:%S")
        return m_ti


def get_number_of_processable_files(root_folder):
    """
    Get the number of processable files in the root folder
    Args:
        root_folder (str): The root folder to start the iteration from.
    Returns:
        int: The number of processable files in the root folder.
    """
    count = 0
    for root, _, files in os.walk(root_folder):
        for file in files:
            if (file.lower().endswith(tuple(VIDEO_EXTENSIONS)) or
                    file.lower().endswith(tuple(IMAGE_EXTENSIONS))):
                count += 1
    return count


def iterate_root_folder(root_folder, function):
    """
    Iterates through the root folder and its subfolders to find image and video files.
    Calls the provided function for each file found.
    Args:
        root_folder (str): The root folder to start the iteration from.
        function (callable): The function to be called for each file found.
            It should take two parameters: root_folder (str) and file_path (str).
    Returns:
        list: A list of results returned by the function for each file found.
    """

    paths = []
    results = []
    for root, _, files in os.walk(root_folder):
        for file in files:
            if (file.lower().endswith(tuple(VIDEO_EXTENSIONS)) or
                    file.lower().endswith(tuple(IMAGE_EXTENSIONS))):
                paths.append(os.path.join(root, file))

    for file_path in tqdm(paths):
        results.append(function(root_folder, file_path))

    return results


def create_date_folder(root_folder, date):
    """
    A function that creates a folder with the given date in the specified root folder.

    Args:
        root_folder (str): The root folder where the new date folder will be created.
        date (str): The name of the date folder to be created.

    Returns:
        str: The path to the newly created date folder.
    """
    date_folder = os.path.join(root_folder, date)
    if not os.path.exists(date_folder):
        os.mkdir(date_folder)
    return date_folder


def check_if_on_correct_folder(root_folder, image_path, creation_date):
    """
    A function that checks if the image is in the correct folder based on the creation date.

    Args:
        root_folder (str): The root folder path.
        image_path (str): The path of the image file.
        creation_date (str): The creation date to compare with the date folder.

    Returns:
        bool: True if the image is in the correct folder, False otherwise.
    """
    date_folder = image_path[len(root_folder) + 1:].split(os.path.sep)[0]
    if date_folder == creation_date:
        return True
    return False


def move_file_to_folder(file_path, date_folder, dont_move_if_exists=False):
    """
    Moves a file to a specified folder.
    :param dont_move_if_exists:  If True, the file will
     not be moved if it already exists in the folder.
    :param file_path: The path of the file to be moved.
    :type file_path: str
    :param date_folder: The path of the folder where the file will be moved.
    :type date_folder: str
    :return: The new path of the moved file, or None if the file
     already exists in the folder.
    :rtype: str or None
    """
    file_name = os.path.basename(file_path)

    if dont_move_if_exists and os.path.exists(os.path.join(date_folder, file_name)):
        return None

    while os.path.exists(os.path.join(date_folder, file_name)):
        file_name_no_extension, file_extension = os.path.splitext(file_name)
        new_name = file_name_no_extension + "_(copy)" + file_extension
        file_name = new_name

    new_path = os.path.join(date_folder, file_name)
    os.rename(file_path, new_path)

    return new_path


def process_file(root_folder, file_path, dont_move_if_exists=False):
    """
    A function that processes a file based on its type and creation date.
    Args:
        root_folder (str): The root folder path.
        file_path (str): The path of the file to be processed.
        dont_move_if_exists (bool):  If True, the file will not
         be moved if it already exists in the folder.
    Returns:
        None if the creation date is None, the new path of the moved file otherwise.
    """

    t_0 = time.perf_counter()
    if file_path.lower().endswith(tuple(IMAGE_EXTENSIONS)):
        creation_date = get_image_creation_date(file_path)
    elif file_path.lower().endswith(tuple(VIDEO_EXTENSIONS)):
        creation_date = get_video_creation_date(file_path)
    else:
        return None

    if creation_date is None:
        destiny_folder = create_date_folder(root_folder, "Unsorted")
        new_path = move_file_to_folder(file_path, destiny_folder, dont_move_if_exists)
        sorter_logger.info(f"Moving {file_path}:"
                           f" to {new_path} - time taken: {time.perf_counter() - t_0:.2f}")

    else:
        creation_date_yyyy_mm = f"{creation_date[:4]}-{creation_date[5:7]}"
        folder_check = check_if_on_correct_folder(root_folder, file_path, creation_date_yyyy_mm)
        if not folder_check:
            destiny_folder = create_date_folder(root_folder, creation_date_yyyy_mm)
            new_path = move_file_to_folder(file_path, destiny_folder, dont_move_if_exists)
            sorter_logger.info(f"Moving {file_path}:"
                               f" to {new_path} - time taken: {time.perf_counter() - t_0:.2f}")
        else:
            destiny_folder = os.path.join(root_folder, creation_date_yyyy_mm)
            sorter_logger.info(f"File {file_path} already in {destiny_folder}"
                               f" - time taken: {time.perf_counter() - t_0:.2f}")
