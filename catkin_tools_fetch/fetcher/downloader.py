"""Hosts a class used to download dependencies.

Attributes:
    log (logging.Log): logger
"""
import logging
import subprocess

from os import path
from subprocess import PIPE

from catkin_tools_fetch.fetcher.tools import Tools

log = logging.getLogger('fetch')


class Downloader(object):
    """Downloader for dependency dict.

    Attributes:
        available_pkgs (str[]): dict of available packages in workspace
        ignore_pkgs (set): a set of packages to ignore (mostly ROS ones).
        ws_path (str): Workspace path. This is where packages live.
    """

    GIT_CHECK_CMD_MASK = "git ls-remote {url}"
    GIT_CLONE_CMD_MASK = "git clone --recursive {url} {path}"

    IGNORE_TAG = "[IGNORED]"
    NOT_FOUND_TAG = "[NOT FOUND]"

    EXISTS_TAG = "[ALREADY EXISTS]"
    CLONED_TAG = "[CLONED]"
    ERROR_TAG = "[ERROR]"

    NO_ERROR = 0

    def __init__(self, ws_path, available_pkgs, ignore_pkgs):
        """Init a downloader.

        Args:
            ws_path (str): Workspace path. This is where packages live.
            available_pkgs (iterable): dict of available packages in workspace.
            ignore_pkgs (iterable): set of packages to ignore (e.g. ROS ones).
        """
        super(Downloader, self).__init__()
        if not path.exists(ws_path):
            raise ValueError("""
            Folder '{}' is missing.
            Are you running 'fetch' from a catkin workspace?
            """.format(ws_path))
        self.ws_path = ws_path
        self.available_pkgs = available_pkgs
        self.ignore_pkgs = ignore_pkgs

    def download_dependencies(self, dep_dict):
        """Check and download dependencies from a dependency dictionary.

        Args:
            dep_dict (dict): dictionary {name: url} with links to repos.

        Returns:
            int: Return code. 0 if all fine. Git error code otherwise.
        """
        if not isinstance(dep_dict, dict):
            raise ValueError("expected a dictionary with dependencies.")
        checked_deps = self.__check_dependencies(dep_dict)
        return self.__clone_dependencies(checked_deps)

    def __clone_dependencies(self, checked_deps):
        """Clone dependencies.

        Args:
            checked_deps (dict): Dict {name: url} with valid urls to repos.

        Returns:
            int: Error code. 0 if all fine, Result from git error otherwise.
        """
        if not checked_deps:
            # exit early if there is nothing to download
            return Downloader.NO_ERROR
        log.info(" Cloning valid dependencies:")
        error_code = Downloader.NO_ERROR
        for name, url in checked_deps.items():
            if name in self.available_pkgs:
                log.info("  %-21s: %s",
                         Tools.decorate(name),
                         Downloader.EXISTS_TAG)
                continue
            dep_path = path.join(self.ws_path, name)
            cmd_clone = Downloader.GIT_CLONE_CMD_MASK.format(
                url=url, path=dep_path)
            try:
                subprocess.check_output(cmd_clone,
                                        stderr=subprocess.STDOUT,
                                        shell=True)
                log.info("  %-21s: %s",
                         Tools.decorate(name),
                         Downloader.CLONED_TAG)
            except subprocess.CalledProcessError as e:
                out_str = e.output.decode("utf8")
                log.debug(" Clone output: %s", out_str)
                if "already exists" in out_str:
                    log.info("  %-21s: %s",
                             Tools.decorate(name),
                             Downloader.EXISTS_TAG)
                else:
                    log.error("  %-21s: %s Git error code: %s",
                              Tools.decorate(name),
                              Downloader.ERROR_TAG,
                              e.returncode)
                    error_code = e.returncode
        return error_code

    def __check_dependencies(self, dep_dict):
        """Check dependencies for validity.

        Args:
            dep_dict (dict): A dictionary {name: url} with dependencies.

        Returns:
            dict: Only valid dependencies from the input dict.
        """
        checked_deps = {}
        if not dep_dict:
            # exit early if there are no new dependencies
            return checked_deps
        log.info(" Checking merged dependencies:")
        for name, url in dep_dict.items():
            if name in self.ignore_pkgs:
                log.info("  %-21s: %s",
                         Tools.decorate(name),
                         Downloader.IGNORE_TAG)
            elif Downloader.repository_exists(url):
                log.info("  %-21s: %s", Tools.decorate(name), url)
                checked_deps[name] = url
            else:
                log.info("  %-21s: %s",
                         Tools.decorate(name),
                         Downloader.NOT_FOUND_TAG)
        return checked_deps

    @staticmethod
    def repository_exists(url):
        """Check if repository exists.

        Uses `git ls-remote` to check if the repository exists.

        Args:
            url (str): Url to check.

        Returns:
            bool: True if exists, False otherwise
        """
        if url == "":
            return False
        git_cmd = Downloader.GIT_CHECK_CMD_MASK.format(url=url)
        try:
            subprocess.check_call(git_cmd, stdout=PIPE,
                                  stderr=PIPE, shell=True)
            return True
        except subprocess.CalledProcessError:
            return False
