import os
import pandas as pd

from PIL import Image
import PIL.ExifTags as ExifTags


def process_base_dirs(base_dirs):
    # md5 hashes of the files we've extracted data for
    files_scanned = set()
    exif_data = []
    if isinstance(base_dirs, str):
        base_dirs = [base_dirs]
    for base_dir in base_dirs:
        print base_dirs
        for root, dirs, files in os.walk(base_dir):
            for file_name in files:
                if file_name.lower().endswith('.jpg'):
                    file_path = os.path.join(root, file_name)
                    img_hash, img_exif = get_exif_data(file_path)
                    if img_hash in files_scanned:
                        continue
                    else:
                        files_scanned.add(img_hash)
                        exif_data.append(img_exif)
    return exif_data


def get_exif_data(file_path):
    img = Image.open(file_path)
    img_hash = hash(tuple(img.getdata()))
    try:
        raw_exif = img._getexif()
    except AttributeError:
        print file_path
    if raw_exif is None:
        return img_hash, {}
    else:
        return img_hash, {ExifTags.TAGS[k]: v for k, v in raw_exif.items()
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
    base_dirs = ['Photos Library.photoslibrary/Masters/2015/05/31']
    base_dirs = [os.path.join(base, dir) for dir in base_dirs]

    rows=['DateTimeOriginal', 'FocalLength', 'Make', 'Model']
    result = make_df(process_base_dirs(base_dirs), rows=rows)

    print result.head()
