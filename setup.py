import argparse
from distutils import log
import os
import site
from stat import ST_MODE
import sys

from setuptools import find_packages
from setuptools import setup
from setuptools.command.install import install

# Setup installation dependencies
install_requires = [
    'catkin-pkg > 0.2.9',
    'catkin_tools >= 0.4.2',
    'setuptools',
]
if sys.version_info[0] == 2 and sys.version_info[1] <= 6:
    install_requires.append('argparse')

# Figure out the resources that need to be installed
this_dir = os.path.abspath(os.path.dirname(__file__))
osx_resources_path = os.path.join(
    this_dir,
    'catkin_tools',
    'notifications',
    'resources',
    'osx',
    'catkin build.app')

setup(
    name='catkin_tools_fetch',
    version='0.0.1',
    packages=find_packages(exclude=['tests', 'docs']),
    install_requires=install_requires,
    author='Igor Bogoslavskyi',
    author_email='igor.bogoslavskyi@uni-bonn.de',
    maintainer='Igor Bogoslavskyi',
    maintainer_email='igor.bogoslavskyi@uni-bonn.de',
    keywords=['catkin'],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
    description="A new verb 'fetch' for catkin_tools",
    long_description="""
Provides a new verb 'fetch' for catkin_tools. Allows fetching dependencies of
the packages found inside the catkin workspace.
""",
    entry_points={
        'catkin_tools.commands.catkin.verbs': [
            'fetch = catkin_fetch:description',
        ],
    },
)
