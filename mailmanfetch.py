#!/usr/bin/env python3

import argparse
import gzip
import logging
import os.path
import re
from datetime import datetime, timezone
from pathlib import Path
from subprocess import run
from urllib.parse import urljoin

import requests
from dateutil.parser import parse

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Download a whole mailman archive.")
    parser.add_argument("archive_url")
    parser.add_argument(
        "local_directory", type=Path, help="Local directory to store the archives."
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Be verbose",
        action="store_const",
        dest="level",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    return parser.parse_args()


def download(archive_url, local_directory, stop_at_first_unmodified=True):
    archives = requests.get(archive_url).text
    gzip_names = re.findall('"[0-9A-Za-z-]+.txt.gz"', archives)
    logging.debug("Downloading archives... found %d months...", len(gzip_names))
    for gzip_name in gzip_names:
        gzip_name = gzip_name[1:-1]
        txt_name = gzip_name.replace(".txt.gz", ".txt")
        last_modified = (
            parse(
                requests.head(urljoin(archive_url, gzip_name)).headers["Last-Modified"]
            )
            .astimezone(timezone.utc)
            .replace(tzinfo=None)
        )
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(local_directory / txt_name))
        except FileNotFoundError:
            mtime = datetime.min
        logging.debug(
            "%s %s (remote mtime: %s, local mtime: %s)",
            "Downloading" if last_modified > mtime else "Skipping",
            gzip_name,
            last_modified,
            mtime,
        )
        if last_modified > mtime:
            with open(local_directory / txt_name, "wb") as f:
                f.write(
                    gzip.decompress(
                        requests.get(urljoin(archive_url, gzip_name)).content
                    )
                )
        elif stop_at_first_unmodified:
            return


def main():
    args = parse_args()
    logging.basicConfig(level=args.level)
    logging.getLogger("urllib3").level = logging.INFO
    if not args.local_directory.exists():
        local_directory.mkdir(parents=True, exist_ok=True)
    download(args.archive_url, args.local_directory)


if __name__ == "__main__":
    main()
