# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

from valohai_local_run import __version__

setup(
    name='valohai-local-run',
    version=__version__,
    entry_points={'console_scripts': ['vh-local-run=valohai_local_run.cli:cli']},
    author='Valohai',
    author_email='hait@valohai.com',
    license='MIT',
    install_requires=[
        'valohai-yaml>=0.5',
    ],
    extras_require={
        'online': [
            'click>=6.0',
            'requests>=2.0.0',
        ],
    },
    packages=find_packages(include=('valohai_local_run*',)),
)
