#!/usr/bin/env python3

from pathlib import Path
from setuptools import setup, find_packages

setup(
    author="Julien Palard",
    author_email="julien@python.org",
    classifiers=[
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Download mailman archives",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    name="mailman-fetch",
    py_modules=["mailmanfetch"],
    version="0.1.2",
    install_requires=["requests", "python-dateutil"],
    extras_require={"dev": ["pylint", "black"]},
    entry_points={"console_scripts": ["mailman-fetch=mailmanfetch:main"]},
)
