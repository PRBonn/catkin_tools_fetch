"""Summary.

Attributes:
    log (TYPE): Description
"""
import logging
import subprocess
from os import path

from catkin_tools_fetch.lib.tools import Tools
from catkin_tools_fetch.lib.tools import GitBridge

log = logging.getLogger('deps')


class Updater(object):
    """Updater class. Handles the updating of all packages."""

    PULLED_TAG = "[PULLED]"
    UP_TO_DATE_TAG = "[UP TO DATE]"
    OK_TAGS = [PULLED_TAG, UP_TO_DATE_TAG]

    CHANGES_TAG = "[UNCOMMITTED CHANGES]"
    NO_TRACK_TAG = "[NO BRANCH]"
    ERROR_TAG = "[GIT ERROR]"
    CONFLICT_TAG = "[MERGE CONFLICT]"

    UP_TO_DATE_MSG = "Already up-to-date"
    CONFLICT_MSG = "Automatic merge failed"

    def __init__(self, ws_path, packages, conflict_strategy):
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
        # some helpful vars
        abort_on_conflict = self.conflict_strategy == Strategy.ABORT
        # stash_on_conflict = self.conflict_strategy == Strategy.STASH
        for ws_folder, package in packages.items():
            log_func = log.info
            picked_tag = None
            folder = path.join(self.ws_path, ws_folder)
            output, branch, has_changes = GitBridge.status(folder)
            if has_changes:
                picked_tag = Updater.CHANGES_TAG
            else:
                try:
                    output = GitBridge.pull(folder, branch)
                    picked_tag = Updater.tag_from_output(output)
                except subprocess.CalledProcessError as e:
                    picked_tag = Updater.ERROR_TAG
                    log.debug(" git pull returned error: %s", e)
            # change logger for warning if something is wrong
            if picked_tag not in Updater.OK_TAGS:
                log_func = log.warning
            # now show the results to the user
            status_msgs.append((package.name, picked_tag))
            log_func("  %-21s: %s", Tools.decorate(package.name), picked_tag)

            # abort if the user wants it
            if abort_on_conflict and log_func == log.warning:
                log.info(" Abort due to picked strategy: '%s'", Strategy.ABORT)
                break
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
