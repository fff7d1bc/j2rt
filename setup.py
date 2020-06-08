#!/usr/bin/env python

from pathlib import Path

from setuptools import setup

from src.j2rt.version import version


setup(
    name="j2rt",
    version=version,
    description="Jinja2 rendering tool",
    long_description=Path('README.rst').read_text(),
    long_description_content_type='text/x-rst',
    author="Piotr Karbowski",
    license="BSD",
    url="https://github.com/slashbeast/j2rt",
    download_url = "https://github.com/slashbeast/j2rt/archive/v{}.tar.gz".format(version),
    install_requires=Path('requirements.txt').read_text().splitlines(),
    package_dir={'j2rt': 'src/j2rt'},
    packages=['j2rt'],
    entry_points={'console_scripts': ['j2rt = j2rt:main']},
)
