import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README')).read()
    CHANGES = open(os.path.join(here, 'CHANGES')).read()
except IOError:
    README = CHANGES = ''

install_requires=[
    'pyramid>=1.0a10',
    ]

setup(name='pyramid_autoroute',
      version='0.1.1',
      description='Pyramid addon to auto detects views',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Framework :: Pyramid",
        ],
      keywords='web wsgi pylons pyramid',
      author="",
      author_email="",
      url="http://docs.pylonsproject.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = install_requires,
      entry_points = """
      """
      )

