"""
Gallery date sorter
"""

import argparse
from utils.utils import iterate_root_folder, process_file

# TODO: Add support to filter just a single folder for speed-up
# TODO: Add support for image/video separate folders
# TODO: Add support for multiprocessing
# TODO: Add to github
# TODO: Add readme
# TODO: Add duplicator remover
# TODO: Add requirements.txt
# TODO: Make executable file

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder", help="Folder to process", required=True)
args = parser.parse_args()

if __name__ == "__main__":
    iterate_root_folder(args.root_path, process_file)
