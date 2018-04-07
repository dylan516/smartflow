#!/usr/bin/env python3
from setuptools import setup, find_packages

__version__ = '1.0.0'

setup(
    name='smartflow',
    version=__version__,
    author='Dylan Liu',
    author_email='dylan.adv@icloud.com',
    url='https://github.com/dylan516/smartflow.git',
    packages=find_packages(),
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=['xlrd'],
    package_data={
        'smartflow': ['.sys']
    },
    description=(
        'Library for generate and edit smartest7 test flow'
    ),
    long_description=(
        'Library for generate and edit smartest7 test flow'
    ),
    platforms=["Any"],
    license='BSD',
    keywords=['testflow', 'smart'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    zip_safe=False,
    include_package_data=True
)
