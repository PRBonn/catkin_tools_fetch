"""Setup module for catkin_tools_fetch."""
import os
import sys
from stat import ST_MODE
from distutils import log
from setuptools import setup
from setuptools import find_packages
from setuptools.command.install import install

version_str = '0.2.0'

# Setup installation dependencies
install_requires = [
    'catkin-pkg > 0.2.9',
    'catkin_tools >= 0.4.2',
    'mock',
    'setuptools',
    'termcolor'
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


class PermissiveInstall(install):
    """A class for permissive install."""

    def run(self):
        """Run the install procedure."""
        install.run(self)
        if os.name == 'posix':
            for file in self.get_outputs():
                # all installed files should be readable for anybody
                mode = ((os.stat(file)[ST_MODE]) | 0o444) & 0o7777
                log.info("changing permissions of %s to %o" % (file, mode))
                os.chmod(file, mode)


github_url = 'https://github.com/niosus/catkin_tools_fetch'

setup(
    name='catkin_tools_fetch',
    packages=find_packages(exclude=['tests', 'docs']),
    version=version_str,
    install_requires=install_requires,
    author='Igor Bogoslavskyi',
    author_email='igor.bogoslavskyi@uni-bonn.de',
    maintainer='Igor Bogoslavskyi',
    maintainer_email='igor.bogoslavskyi@uni-bonn.de',
    keywords=['catkin', 'catkin_tools'],
    license="Apache 2.0",
    url=github_url,
    download_url=github_url + '/tarball/' + version_str,
    classifiers=[
        'Environment :: Console',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
    ],
    description="""A new verb 'dependencies' to manage project dependencies with
catkin_tools""",
    long_description="""Provides a new verb 'dependencies' or 'deps' for
catkin_tools. Allows fetching dependencies of the packages found inside the
catkin workspace and updating all the packages to the final state.""",
    test_suite='tests',
    entry_points={
        'catkin_tools.commands.catkin.verbs': [
            'fetch = catkin_tools_fetch:description',
            'deps = catkin_tools_fetch:description_deps',
            'dependencies = catkin_tools_fetch:description_dependencies',
        ],
    },
    cmdclass={'install': PermissiveInstall},
)
