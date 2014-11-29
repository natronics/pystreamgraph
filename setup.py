#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pystreamgraph

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='pystreamgraph',
    version=pystreamgraph.__version__,
    description='A simple way to generate stream graphs using python.',
    long_description=readme + '\n\n' + history,
    author='Nathan Bergey',
    author_email='nathan.bergey@gmail.com',
    url='https://github.com/natronics/pytstreamgraph',
    packages=[
        'pystreamgraph',
    ],
    package_dir={'pystreamgraph': 'pystreamgraph'},
    include_package_data=True,
    install_requires=[
    ],
    license="GPLv3",
    zip_safe=False,
    keywords='streamgraph stream graph charts timeseries',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
)
