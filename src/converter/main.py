import glob
import os
import shutil
import json

from PIL import Image
from PIL.ExifTags import TAGS
from PIL.TiffImagePlugin import IFDRational
from datetime import datetime
from dateutil.tz import tz

ORIGINAL_FOLDER = "org"
DESTINATION_FOLDER_IMG = "converted/imgs/"
DESTINATION_FOLDER_METADATA = "converted/metadata/"
DATE_FIELD = "DateTimeDigitized"
DATE_FORMAT = "%Y:%m:%d %H:%M:%S"
PHOTO_TIMEZONE = tz.gettz("Canada/Eastern")


def convert_to_epoch(date):
    local_time = datetime.strptime(date, DATE_FORMAT)
    local_time = local_time.replace(tzinfo=PHOTO_TIMEZONE)
    utc_time = local_time.astimezone(tz.tzutc())
    return int(utc_time.timestamp())


def _make_json_serializable(x):
    if isinstance(x, IFDRational):
        return (
            float("inf")
            if x._denominator == 0
            else x._numerator / x._denominator
        )
    elif isinstance(x, bytes):
        return x.decode("utf-8")
    return x


def make_json_serializable(x):
    if isinstance(x, dict):
        for k, v in x.items():
            x[k] = make_json_serializable(v)
        return x
    if isinstance(x, list) or isinstance(x, tuple):
        z = [_make_json_serializable(y) for y in x]
        return list(z) if isinstance(x, list) else tuple(z)
    return _make_json_serializable(x)


def get_metadata(path):
    metadata = {}
    exifdata = Image.open(path).getexif()
    for tag_id in exifdata:
        tag = TAGS.get(tag_id, tag_id)
        data = exifdata.get(tag_id)
        if isinstance(data, bytes):
            data = data.decode()
        metadata[tag] = data
    return make_json_serializable(metadata)


def main():
    count = 0
    for file in glob.glob(f"{ORIGINAL_FOLDER}/*"):
        count += 1
        print(f"Processing {file}...")
        metadata = get_metadata(file)
        epoch = convert_to_epoch(metadata[DATE_FIELD])
        # copy file
        shutil.copy2(file, DESTINATION_FOLDER_IMG + f"{epoch}.jpg")
        # copy metadata
        json.dump(
            metadata,
            open(DESTINATION_FOLDER_METADATA + f"{epoch}.json", "w+"),
            indent=4,
        )
    print(f"Processed {count} files.")


if __name__ == "__main__":
    main()
