#!/usr/bin/env python3

"""Short program to help mirroring GNU Mailman archives.
"""

import argparse
import gzip
import logging
import os.path
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from dateutil.parser import parse

__version__ = "0.1.2"
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Download a whole mailman archive.")
    parser.add_argument("archive_url")
    parser.add_argument(
        "local_directory", type=Path, help="Local directory to store the archives."
    )
    parser.add_argument(
        "-n",
        "--numeric",
        action="store_true",
        help="Use numeric months instead of their names. "
        "It helps as it's naturally ordered.",
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
    parser.add_argument("-a", "--all", help="Recrawl all history", action="store_true")
    return parser.parse_args()


def replace_month_name_to_number(txt_name):
    """In a mailman archive file name, like "2018-January.txt", replace
    the month, "January", by its numerical value, "01".
    """
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    year, month_name, ext = re.split("[.-]", txt_name)
    return "{}-{:02d}.{}".format(year, months.index(month_name) + 1, ext)


def download(
    archive_url, local_directory, numeric=False, stop_at_first_unmodified=True
):
    """Download mailman archives at archive_url into local_directory.
    """
    archives = requests.get(archive_url).text
    gzip_names = re.findall('"[0-9A-Za-z-]+.txt.gz"', archives)
    logging.debug("Downloading archives... found %d months...", len(gzip_names))
    for gzip_name in gzip_names:
        gzip_name = gzip_name[1:-1]
        txt_name = gzip_name.replace(".txt.gz", ".txt")
        if numeric:
            txt_name = replace_month_name_to_number(txt_name)
        if stop_at_first_unmodified:
            last_modified = (
                parse(
                    requests.head(urljoin(archive_url, gzip_name)).headers[
                        "Last-Modified"
                    ]
                )
                .astimezone(timezone.utc)
                .replace(tzinfo=None)
            )
            try:
                mtime = datetime.fromtimestamp(
                    os.path.getmtime(str(local_directory / txt_name))
                )
            except FileNotFoundError:
                mtime = datetime.min
            logging.debug(
                "%s %s (remote mtime: %s, local mtime: %s)",
                "Downloading" if last_modified > mtime else "Skipping",
                gzip_name,
                last_modified,
                mtime,
            )
        if not stop_at_first_unmodified or last_modified > mtime:
            with open(str(local_directory / txt_name), "wb") as f:
                f.write(
                    gzip.decompress(
                        requests.get(urljoin(archive_url, gzip_name)).content
                    )
                )
        elif stop_at_first_unmodified:
            return


def main():
    """CLI script entry point.
    """
    args = parse_args()
    logging.basicConfig(level=args.level)
    logging.getLogger("urllib3").level = logging.INFO
    if not args.local_directory.exists():
        args.local_directory.mkdir(parents=True, exist_ok=True)
    download(args.archive_url, args.local_directory, args.numeric, not args.all)


if __name__ == "__main__":
    main()
