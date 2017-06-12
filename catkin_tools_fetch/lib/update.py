"""Summary.

Attributes:
    log (TYPE): Description
"""
import logging
import subprocess
from os import path
from termcolor import colored
from concurrent import futures

from catkin_tools_fetch.lib.tools import Tools
from catkin_tools_fetch.lib.tools import GitBridge
from catkin_tools_fetch.lib.printer import Printer

log = logging.getLogger('deps')


class Updater(object):
    """Updater class. Handles the updating of all packages."""

    PULLED_TAG = "[PULLED]"
    UP_TO_DATE_TAG = "[UP TO DATE]"
    OK_TAGS = [PULLED_TAG, UP_TO_DATE_TAG]

    CHANGES_TAG = "[UNCOMMITTED CHANGES]"
    RUNNING_TAG = "[RUNNING]"
    NO_TRACK_TAG = "[NO BRANCH]"
    ERROR_TAG = "[GIT ERROR]"
    CONFLICT_TAG = "[MERGE CONFLICT]"

    UP_TO_DATE_MSG = "Already up-to-date"
    CONFLICT_MSG = "Automatic merge failed"

    def __init__(self,
                 ws_path,
                 packages,
                 conflict_strategy,
                 use_preprint=True,
                 colored=True,
                 num_threads=4):
        """Initialize the updater.

        Args:
            ws_path (str): Path to the workspace
            packages (dict(str)): Dictionary of packages to be downloaded
            conflict_strategy (str): A strategy to handle conflicts
        """
        super(Updater, self).__init__()
        self.ws_path = ws_path
        self.packages = packages
        self.conflict_strategy = conflict_strategy
        self.thread_pool = futures.ThreadPoolExecutor(max_workers=num_threads)
        self.printer = Printer()
        self.colored = colored
        self.use_preprint = use_preprint

    def filter_packages(self, selected_packages):
        """Filter the packages based on user input.

        Args:
            selected_packages (str[]): List of package names picked by the user

        Returns:
            dict: A dictionary of packages that match selected_packages.
        """
        if not selected_packages:
            return self.packages
        filtered_packages = {}
        for ws_folder, package in self.packages.items():
            if package.name in selected_packages:
                filtered_packages[ws_folder] = package
        return filtered_packages

    def pick_tag(self, folder, package):
        """Pick result tag for a folder."""
        if self.use_preprint:
            msg = " {}: {}".format(Tools.decorate(
                package.name), Updater.RUNNING_TAG)
            self.printer.add_msg(package.name, msg)
        output, branch, has_changes = GitBridge.status(folder)
        if has_changes:
            return package, Updater.CHANGES_TAG
        try:
            output = GitBridge.pull(folder, branch)
            return package, Updater.tag_from_output(output)
        except subprocess.CalledProcessError as e:
            log.debug(" git pull returned error: %s", e)
            return package, Updater.ERROR_TAG

    def update_packages(self, selected_packages):
        """Update all the folders to match the remote. Considers the branch.

        Args:
            selected_packages (str[]): List of packages picked by the user.

        Returns:
            status_msgs (list(tuple)): return a list of tupples (pkg_name, tag)
        """
        log.info(" Pulling packages:")
        packages = self.filter_packages(selected_packages)
        status_msgs = []
        futures_list = []
        for ws_folder, package in packages.items():
            picked_tag = None
            folder = path.join(self.ws_path, ws_folder)
            futures_list.append(
                self.thread_pool.submit(self.pick_tag, folder, package))
        for future in futures.as_completed(futures_list):
            package, picked_tag = future.result()
            # change logger for warning if something is wrong
            if self.colored:
                picked_tag = Updater.colorize_tag(picked_tag)
            # now show the results to the user
            status_msgs.append((package.name, picked_tag))
            msg = " {}: {}".format(Tools.decorate(package.name), picked_tag)
            self.printer.purge_msg(package.name, msg)
        return status_msgs

    @staticmethod
    def tag_from_output(output):
        """Get tag from output."""
        try:
            str_output = output.decode("utf-8")
        except AttributeError:
            str_output = output
        if Updater.UP_TO_DATE_MSG in str_output:
            return Updater.UP_TO_DATE_TAG
        if Updater.CONFLICT_MSG in str_output:
            return Updater.CONFLICT_TAG
        return Updater.PULLED_TAG

    @staticmethod
    def colorize_tag(picked_tag):
        """Colorize the tag."""
        if picked_tag in Updater.OK_TAGS:
            return colored(picked_tag, 'green')

        if picked_tag == Updater.CHANGES_TAG:
            # this is a warning
            return colored(picked_tag, 'yellow')
        return colored(picked_tag, 'red')


class Strategy(object):
    """An enum of stategies for update."""

    IGNORE = 'ignore'
    ABORT = 'abort'
    # STASH = 'stash'

    @classmethod
    def list_all(cls):
        """List all strategies."""
        all_strategies = [val for key, val in cls.__dict__.items()
                          if not callable(getattr(cls, key))
                          and not key.startswith("__")]
        return all_strategies
