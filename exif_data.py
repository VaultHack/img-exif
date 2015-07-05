import os
import hashlib

import pandas as pd
from PIL import Image
import PIL.ExifTags as ExifTags


def process_base_dirs(base_dirs):
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
    for file_path in file_paths:
        md5 = get_md5(file_path)
        if md5 not in files_scanned:
            files_scanned.add(md5)
            exif_data.append(get_exif_data(file_path))


def get_md5(file_path, block_size=2**20):
    m = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            buf = f.read(block_size)
            if not buf:
                break
            m.update(buf)
    return m.digest()


def get_exif_data(file_path):
    img = Image.open(file_path)
    raw_exif = img._getexif()
    if raw_exif is None:
        return {}
    else:
        return {ExifTags.TAGS[k]: v for k, v in raw_exif.items()
                if k in ExifTags.TAGS}


def get_df(base_dirs, rows='FocalLength'):
    if isinstance(rows, str):
        rows = [rows]
    exif_data = process_base_dirs(base_dirs)
    result_dict = {row: [] for row in rows}

    for exif in exif_data:
        for row in rows:
            result_dict[row].append(exif.get(row))

    return pd.DataFrame(result_dict)

if __name__ == '__main__':
    base = os.path.join('/Users/frank/Pictures',
                        'Photos Library.photoslibrary/Masters/2015/05/31')

    result = get_df(base,
                    rows=['DateTimeOriginal', 'FocalLength', 'Make', 'Model'])

    print result.head()
