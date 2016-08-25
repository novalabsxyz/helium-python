#!/usr/bin/env python
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


__version__ = ''
with open('helium/__about__.py', 'r') as fd:
    reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
    for line in fd:
        m = reg.match(line)
        if m:
            __version__ = m.group(1)
            break

if not __version__:
    raise RuntimeError('Cannot find version information')

version = __version__
authors = 'Marc Nijdam'
emails = ''
packages = ['helium']
requires = [
    "future>=0.15",
    "requests>=2.9",
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
    license='BSD',
)
