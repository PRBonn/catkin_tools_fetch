import os
import sys
from stat import ST_MODE
from distutils import log
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


class PermissiveInstall(install):

    def run(self):
        install.run(self)
        if os.name == 'posix':
            for file in self.get_outputs():
                # all installed files should be readable for anybody
                mode = ((os.stat(file)[ST_MODE]) | 0o444) & 0o7777
                log.info("changing permissions of %s to %o" % (file, mode))
                os.chmod(file, mode)

        # Provide information about bash completion after default install.
        if (sys.platform.startswith("linux") and
                self.install_data == "/usr/local"):
            log.info("""
----------------------------------------------------------------
To enable tab completion, add the following to your '~/.bashrc':
  source {0}
----------------------------------------------------------------
""".format(os.path.join(self.install_data,
                        'etc/bash_completion.d',
                        'catkin_tools-completion.bash')))


setup(
    name='catkin_tools_fetch',
    version='0.0.1',
    packages=find_packages(exclude=['tests', 'docs']),
    install_requires=install_requires,
    author='Igor Bogoslavskyi',
    author_email='igor.bogoslavskyi@uni-bonn.de',
    maintainer='Igor Bogoslavskyi',
    maintainer_email='igor.bogoslavskyi@uni-bonn.de',
    keywords=['catkin', 'catkin_tools'],
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
    test_suite='tests',
    entry_points={
        'catkin_tools.commands.catkin.verbs': [
            'fetch = catkin_fetch:description',
        ],
    },
    cmdclass={'install': PermissiveInstall},
)
