#!/usr/bin/env python3

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='iwallpaper',
    version='0.0.1',
    description='An Intelligent Wallpaper Manager',
    long_description=long_description,
    url='https://github.com/bibaijin/iwallpaper',
    author='bibaijin',
    author_email='bibaijin@gmail.com',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['requests>=2.18'],
    entry_points={
        'console_scripts': [
            'iwallpaper=iwallpaper:main',
        ],
    },
)