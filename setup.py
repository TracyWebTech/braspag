#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from braspag.version import __version__

readme = open('README.md').read()

setup(
    name='braspag',
    version=__version__,
    description = "Python library to consume Braspag SOAP Web services",
    long_description = readme,
    packages=['braspag'],
    package_data = {
        'braspag': ['templates/*.xml'],
    },
    install_requires=['Jinja2'],
    tests_require=['Mock'],
)
