#!/usr/bin/env python

from setuptools import setup
from pathlib import Path


setup(
    name="j2rt",
    version='0.0.2',
    description="Jinja2 rendering tool",
    long_description=Path('README.rst').read_text(),
    long_description_content_type='text/x-rst',
    install_requires=Path('requirements.txt').read_text().splitlines(),
    package_dir={'j2rt': 'src/j2rt'},
    packages=['j2rt'],
    entry_points={'console_scripts': ['j2rt = j2rt:main']},
)
