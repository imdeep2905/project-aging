"""
Migration Info

Initially I used to extract exif data by myself using PIL.
Now that I have discovered exif package, this migration script
converts all old metadata to the new format.
"""

import json
import os
import glob
from exif import Image


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
    os.makedirs("out/imgs", exist_ok=True)
    os.makedirs("out/metadata", exist_ok=True)

    count = 0
    for file in glob.glob("in/imgs/*"):
        count += 1
        print(f"Processing {file}...")
        metadata = get_metadata(file)
        # copy metadata
        json.dump(
            metadata,
            open(
                "out/metadata/" + f"{file.split('/')[-1].split('.')[0]}.json",
                "w+",
            ),
            indent=4,
        )
    print(f"Processed {count} files.")


if __name__ == "__main__":
    main()
