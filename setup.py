#!/usr/bin/env python

from setuptools import setup
from pathlib import Path


def get_requirements():
    return Path('requirements.txt').read_text().splitlines()


setup(
    name="j2rt",
    version='0.0.1',
    install_requires=get_requirements(),
    package_dir={'j2rt': 'src/j2rt'},
    packages=['j2rt'],
    entry_points={'console_scripts': ['j2rt = j2rt:main']},
)
