import os
import hashlib
import pandas as pd

from PIL import Image
import PIL.ExifTags as ExifTags


def process_base_dirs(base_dirs):
    # md5 hashes of the files we've extracted data for
    files_scanned = set()
    exif_data = []
    for base_dir in [base_dirs]:
        for root, dirs, files in os.walk(base_dir):
            for file_name in files:
                if file_name.lower().endswith('.jpg'):
                    file_path = os.path.join(root, file_name)
                    md5 = get_md5(file_path)
                    if md5 in files_scanned:
                        continue
                    else:
                        files_scanned.add(md5)
                        exif_data.append(get_exif_data(file_path))
    return exif_data

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


def make_df(exif_data, rows=('FocalLength')):
    result_dict = {row: [] for row in rows}
    for exif in exif_data:
        for row in rows:
            result_dict[row].append(exif.get(row))
    return pd.DataFrame(result_dict)


def get_df(base_dirs, rows=('FocalLength')):
    return make_df(process_base_dirs(base_dirs), rows=rows)

if __name__ == '__main__':
    base = '/Users/frank/Pictures'
    base_dirs = ['Photos Library.photoslibrary/Masters/2015/03/21']
    base_dirs = [os.path.join(base, dir) for dir in base_dirs]

    rows=['DateTimeOriginal', 'FocalLength', 'Make', 'Model']
    result = make_df(process_base_dirs(base_dirs), rows=rows)

    print result.head()

