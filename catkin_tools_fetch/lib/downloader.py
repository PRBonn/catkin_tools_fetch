"""Hosts a class used to download dependencies.

Attributes:
    log (logging.Log): logger
"""
import logging

from os import path
from termcolor import colored
from concurrent import futures

from catkin_tools_fetch.lib.tools import Tools
from catkin_tools_fetch.lib.tools import GitBridge
from catkin_tools_fetch.lib.printer import Printer

log = logging.getLogger('deps')


class Downloader(object):
    """Downloader for dependency dict.

    Attributes:
        available_pkgs (str[]): dict of available packages in workspace
        ignore_pkgs (set): a set of packages to ignore (mostly ROS ones).
        ws_path (str): Workspace path. This is where packages live.
    """

    IGNORE_TAG = colored("[IGNORED]", 'yellow')
    NOT_FOUND_TAG = colored("[NOT FOUND]", 'red')
    CLONING_TAG = "[CLONING]"
    CHECKING_TAG = "[CHECKING]"

    NO_ERROR = 0

    def __init__(self,
                 ws_path,
                 available_pkgs,
                 ignore_pkgs,
                 use_preprint=True,
                 num_threads=4):
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
        self.thread_pool = futures.ThreadPoolExecutor(max_workers=num_threads)
        self.use_preprint = use_preprint
        self.printer = Printer()

    def download_dependencies(self, dep_dict):
        """Check and download dependencies from a dependency dictionary.

        Args:
            dep_dict (dict): dictionary {name: dep} with dependencies.

        Returns:
            int: Return code. 0 if all fine. Git error code otherwise.
        """
        if not isinstance(dep_dict, dict):
            raise ValueError("expected a dictionary with dependencies.")
        for dep in dep_dict.values():
            log.debug(" dep before: %s", dep)
        checked_deps = self.__check_dependencies(dep_dict)
        return self.__clone_dependencies(checked_deps)

    def __clone_dependency(self, pkg_name, url, dep_path, branch):
        """Clone a single dependency. Return a future to the clone process."""
        if self.use_preprint:
            msg = " {}: {}".format(Tools.decorate(pkg_name),
                                   Downloader.CLONING_TAG)
            self.printer.add_msg(pkg_name, msg)
        return GitBridge.clone(pkg_name, url, dep_path, branch)

    def __clone_dependencies(self, checked_deps):
        """Clone dependencies.

        Args:
            checked_deps (dict): Dict {name: dep} with valid dependencies.

        Returns:
            int: Error code. 0 if all fine, Result from git error otherwise.
        """
        if not checked_deps:
            # exit early if there is nothing to download
            return Downloader.NO_ERROR
        log.info(" Cloning valid dependencies:")
        error_code = Downloader.NO_ERROR
        # store all tasks in a futures list
        futures_list = []
        for name, dependency in checked_deps.items():
            url = dependency.url
            branch = dependency.branch
            log.debug(" prepare clone: url: %s, branch: %s", url, branch)
            if not branch:
                branch = "master"
            if name in self.available_pkgs:
                msg = " {}: {}".format(
                    Tools.decorate(name), GitBridge.EXISTS_TAG)
                self.printer.purge_msg(name, msg)
                continue
            dep_path = path.join(self.ws_path, name)
            future = self.thread_pool.submit(
                self.__clone_dependency, name, url, dep_path, branch)
            futures_list.append(future)
        # we have all the futures ready. Now just wait for them to finish.
        for future in futures.as_completed(futures_list):
            pkg_name, clone_result = future.result()
            msg = " {}: {}".format(
                Tools.decorate(pkg_name), clone_result)
            self.printer.purge_msg(pkg_name, msg)
            if clone_result == GitBridge.ERROR_TAG:
                error_code = 1
        return error_code

    def __check_dependency(self, dependency):
        if self.use_preprint:
            msg = " {}: {}".format(
                Tools.decorate(dependency.name), Downloader.CHECKING_TAG)
            self.printer.add_msg(dependency.name, msg)
        return GitBridge.repository_exists(dependency)

    def __check_dependencies(self, dep_dict):
        """Check dependencies for validity.

        We don't want to avoid packages that we ignore or those which
        repositories do not exist.

        Args:
            dep_dict (dict): A dictionary {name: dep} with dependencies.

        Returns:
            dict: Only valid dependencies from the input dict.
        """
        checked_deps = {}
        if not dep_dict:
            # exit early if there are no new dependencies
            return checked_deps
        futures_list = []
        log.info(" Checking merged dependencies:")
        for dependency in dep_dict.values():
            log.debug(" check dep: %s", dependency)
            if dependency.name in self.ignore_pkgs:
                msg = " {}: {}".format(
                    Tools.decorate(dependency.name), Downloader.IGNORE_TAG)
                self.printer.add_msg(dependency.name, msg)
                continue
            futures_list.append(self.thread_pool.submit(
                self.__check_dependency, dependency))
        for future in futures.as_completed(futures_list):
            dependency, repo_found = future.result()
            if repo_found:
                msg = " {}: {}".format(
                    Tools.decorate(dependency.name), dependency.url)
                self.printer.purge_msg(dependency.name, msg)
                checked_deps[dependency.name] = dependency
            else:
                msg = " {}: {}".format(
                    Tools.decorate(dependency.name), Downloader.NOT_FOUND_TAG)
                self.printer.purge_msg(dependency.name, msg)
        return checked_deps
