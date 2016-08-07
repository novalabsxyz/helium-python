"""The module that holds metadata about this library."""

from __future__ import unicode_literals

__package_name__ = 'helium-python'
__title__ = 'helium'
__author__ = 'Helium'
__author_email__ = 'hello@helium.com'
__license__ = 'BSD'
__copyright__ = 'Copyright 2016 Helium'
__version__ = '0.1.0'
__version_info__ = tuple(int(i) for i in __version__.split('.') if i.isdigit())
__url__ = 'http://helium-python.readthedocs.org'

__all__ = (
    '__package_name__', '__title__', '__author__', '__author_email__',
    '__license__', '__copyright__', '__version__', '__version_info__',
    '__url__',
)
