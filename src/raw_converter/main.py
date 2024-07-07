import glob
import shutil
import json

from timezonefinder import TimezoneFinder
from exif import Image
from datetime import datetime
from dateutil.tz import tz

ORIGINAL_FOLDER = "org"
DESTINATION_FOLDER_IMG = "converted/imgs/"
DESTINATION_FOLDER_METADATA = "converted/metadata/"
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
        print(
            "Latitude or Longitude not found."
            f" Using default timezone '{DEFAULT_TIMEZONE}'",
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


def main():
    count = 0
    for file in glob.glob(f"{ORIGINAL_FOLDER}/*"):
        count += 1
        print(f"Processing {file}...")
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
    print(f"Processed {count} files.")


if __name__ == "__main__":
    main()
