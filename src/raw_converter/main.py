import glob
import os
import shutil
import json
from click import secho
from timezonefinder import TimezoneFinder
from exif import Image
from datetime import datetime
from dateutil.tz import tz

ORIGINAL_FOLDER = None
DESTINATION_FOLDER_IMG = "out/raw_converter/imgs/"
DESTINATION_FOLDER_METADATA = "out/raw_converter/metadata/"
DATE_FORMAT = "%Y:%m:%d %H:%M:%S"
DEFAULT_TIMEZONE = "America/Toronto"


def get_epoch_from_metadata(metadata):
    try:
        lat_h, lat_m, lat_s = metadata["gps_latitude"]
        lng_h, lng_m, lng_s = metadata["gps_longitude"]

        lat = lat_h + lat_m / 60 + lat_s / 3600
        lng = lng_h + lng_m / 60 + lng_s / 3600

        timezone = TimezoneFinder().timezone_at(lat=lat, lng=lng)
    except KeyError:
        timezone = DEFAULT_TIMEZONE
        secho(
            "Latitude or Longitude not found."
            f" Using default timezone '{DEFAULT_TIMEZONE}'",
            fg="yellow",
        )

    tz_timezone = tz.gettz(timezone)
    local_time = datetime.strptime(metadata["datetime_digitized"], DATE_FORMAT)
    local_time = local_time.replace(tzinfo=tz_timezone)
    utc_time = local_time.astimezone(tz.tzutc())
    return int(utc_time.timestamp())


def get_metadata(path):
    with open(path, "rb") as f:
        img = Image(f)
    metadata = {}
    for k in img.list_all():
        try:
            metadata[k] = img.get(k)
        except Exception:
            pass
    metadata.pop("flash")
    return metadata


def main(dir, default_tz):
    global ORIGINAL_FOLDER
    global DEFAULT_TIMEZONE
    ORIGINAL_FOLDER = dir
    DEFAULT_TIMEZONE = default_tz

    for dir in [DESTINATION_FOLDER_IMG, DESTINATION_FOLDER_METADATA]:
        os.makedirs(dir, exist_ok=True)

    secho(f"Using input directory: {dir}", fg="green")
    count = 0
    for file in glob.glob(f"{ORIGINAL_FOLDER}/*"):
        count += 1
        secho(f"Processing {file}...", fg="white")
        metadata = get_metadata(file)
        epoch = get_epoch_from_metadata(metadata)
        # copy file
        shutil.copy2(file, DESTINATION_FOLDER_IMG + f"{epoch}.jpg")
        # copy metadata
        json.dump(
            metadata,
            open(DESTINATION_FOLDER_METADATA + f"{epoch}.json", "w+"),
            indent=4,
        )
    secho(f"Processed {count} files.", fg="green")
