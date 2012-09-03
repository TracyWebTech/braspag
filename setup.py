#!/usr/bin/python                                                                
# -*- coding: utf-8 -*-

from setuptools import setup
from braspag import __version__

setup(
    name='braspag',
    version=__version__,
    packages=['braspag'],
    package_data = {
        'braspag': ['templates/*.xml'],
#        'braspag/templates/authorize.xml'
    },
    install_requires=['Jinja2']
)
