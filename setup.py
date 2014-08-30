#!/usr/bin/env python
# Copyright (C) 2014 Jurriaan Bremer.
# This file is part of HorseMPDC - http://www.horsempdc.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='HorseMPDC',
    version='0.1.0',
    author='Jurriaan Bremer',
    author_email='jurriaanbremer@gmail.com',
    packages=[
        'horsempdc',
    ],
    scripts=[
        'bin/horsempdc',
    ],
    url='http://pypi.python.org/pypi/horsempdc/',
    license='docs/LICENSE.txt',
    description='Horse interface for MPD daemons such as Mopidy.',
    include_package_data=True,
    install_requires=[
        # Required on BSD systems for unknown reasons.
        'jinja2',

        # Required for interaction with MPD daemons.
        'requests',
        'requests-toolbelt',
    ],
)
