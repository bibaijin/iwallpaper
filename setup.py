#!/usr/bin/env python3

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='iwallpaper',
    version='1.0.1',
    description='An Intelligent Wallpaper Manager',
    long_description=long_description,
    url='https://github.com/bibaijin/iwallpaper',
    author='bibaijin',
    author_email='bibaijin@gmail.com',
    packages=['iwallpaper'],
    data_files=[('iwallpaper', ['iwallpaper/favicon.ico'])],
    install_requires=[
        'lxml>=4.1', 'matplotlib>=2.2', 'numpy>=1.14', 'opencv-python>=3.4',
        'peewee>=3.1', 'pytest>=3.4', 'requests>=2.18', 'scipy>=1.0',
        'wxPython>=4.0'
    ],
    entry_points={
        'console_scripts': [
            'iwallpaper=iwallpaper.main:main',
        ],
    },
)
