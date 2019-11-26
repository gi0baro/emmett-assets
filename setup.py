# -*- coding: utf-8 -*-
"""
Emmett-Assets
-------------

Integrates the ``webassets`` library with Emmett, adding support for
merging, minifying and compiling CSS and Javascript files.
"""

import re

from setuptools import find_packages, setup

with open('emmett_assets/__init__.py', 'r', encoding='utf8') as f:
    version = re.search(r'__version__ = "(.*?)"', f.read(), re.M).group(1)


setup(
    name='Emmett-Assets',
    version=version,
    url='https://github.com/gi0baro/emmett-assets',
    license='BSD-3-Clause',
    author='Giovanni Barillari',
    author_email='gi0baro@d4net.org',
    description='Assets management for Emmett',
    long_description=__doc__,
    packages=find_packages(),
    python_requires='>=3.7',
    include_package_data=True,
    install_requires=[
        'emmett',
        'PyExecJS==1.3.1',
        'CoffeeScript',
        'jsmin',
        'cssmin',
        'libsass'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
