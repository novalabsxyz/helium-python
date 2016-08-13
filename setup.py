#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = '0.1'
authors = 'Marc Nijdam'
emails = ''
packages = ['helium']
requires = [
    "future>=0.15",
    "requests==2.10.0",
    "uritemplate>=0.6",
    "inflection>=0.3",
]

setup(
    name='helium-python',
    version=version,
    description='Wrapper for the Helium API',
    long_description="Python toolkit for working with the Helium API",
    author=authors,
    author_email=emails,
    url='https://github.com/helium/helium-python',
    packages=packages,
    install_requires=requires,
    license='MIT',
)
