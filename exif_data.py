import os
import hashlib

import pandas as pd
from PIL import Image
import PIL.ExifTags as ExifTags


def process_base_dirs(base_dirs):
    """Extract exif data from all jpg files under the provided directory(ies)

    :param base_dirs: path or paths to directories to scan all files under
    :return: A list of dictionaries containing exif data for each file
    """
    files_scanned = set()
    exif_data = []

    if isinstance(base_dirs, str):
        base_dirs = [base_dirs]

    for base_dir in base_dirs:
        for root, dirs, files in os.walk(base_dir):
            jpgs = [os.path.join(root, file_name) for file_name in files
                    if file_name.lower().endswith('.jpg')]
            process_files(jpgs, files_scanned, exif_data)

    return exif_data


def process_files(file_paths, files_scanned, exif_data):
    """Extract exif data from each of the provided files, avoiding duplicates

    :param file_paths: Files to extract data from
    :param files_scanned: Set of hashes of file data
    :param exif_data: List of dictionaries of exif data
    """
    for file_path in file_paths:
        md5 = get_md5(file_path)
        if md5 not in files_scanned:
            files_scanned.add(md5)
            exif_data.append(get_exif_data(file_path))


def get_md5(file_path, block_size=2**20):
    """Return The md5 hash of the file's data."""
    m = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            buf = f.read(block_size)
            if not buf:
                break
            m.update(buf)
    return m.digest()


def get_exif_data(file_path):
    """Extract a dict of exif data from the provided file"""
    img = Image.open(file_path)
    raw_exif = img._getexif()
    if raw_exif is None:
        return {}
    else:
        return {ExifTags.TAGS[k]: v for k, v in raw_exif.items()
                if k in ExifTags.TAGS}


def make_df(base_dirs,
            columns=('DateTimeOriginal', 'FocalLength', 'Make', 'Model')):
    """Return a dataframe of exif data from all the files under the directories
    provided in base_dirs.

    :param base_dirs: path or paths to scan all files under
    :param columns: fields of exif data to extract
    :return: DataFrame
    """
    exif_data = process_base_dirs(base_dirs)
    result_dict = {column: [] for column in columns}

    for exif in exif_data:
        for column in columns:
            result_dict[column].append(exif.get(column))

    return pd.DataFrame(result_dict)

if __name__ == '__main__':
    base = os.path.join('/Users/frank/Pictures',
                        'Photos Library.photoslibrary/Masters/2015/05/31')
    result = make_df(base)

    print result.head()
