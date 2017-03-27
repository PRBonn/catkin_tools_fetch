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

    CHANGES_TAG = "[UNCOMMITTED CHANGES]"
    NO_TRACK_TAG = "[NO BRANCH]"
    UP_TO_DATE_TAG = "[UP TO DATE]"
    PULLED_TAG = "[PULLED]"
    ERROR_TAG = "[GIT ERROR]"
    CONFLICT_TAG = "[MERGE CONFLICT]"

    UP_TO_DATE_MSG = "Already up-to-date"
    CONFLICT_MSG = "Automatic merge failed"

    OK_TAGS = [PULLED_TAG, UP_TO_DATE_TAG]

    def __init__(self, ws_path, packages, conflict_strategy):
        """Initialize the updater.

        Args:
            ws_path (str): Path to the workspace
            packages (TYPE): Description
            conflict_strategy (TYPE): Description
        """
        super(Updater, self).__init__()
        self.ws_path = ws_path
        self.packages = packages
        self.conflict_strategy = conflict_strategy

    def filter_packages(self, selected_packages):
        """Filter the packages based on user input.

        Args:
            selected_packages (str[]): List of pacakges picker by the user.

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
        """
        log.info(" Pulling packages:")
        packages = self.filter_packages(selected_packages)
        for ws_folder, package in packages.items():
            folder = path.join(self.ws_path, ws_folder)
            output, branch, has_changes = GitBridge.status(folder)
            if has_changes:
                log.info("  %-21s: %s", Tools.decorate(package.name),
                         Updater.CHANGES_TAG)
                continue
            try:
                output = GitBridge.pull(folder, branch)
                tag = Updater.tag_from_output(output)
                log_func = log.info
                if tag not in Updater.OK_TAGS:
                    log_func = log.warning
                log_func("  %-21s: %s", Tools.decorate(package.name), tag)
            except subprocess.CalledProcessError as e:
                log.error("  %-21s: %s",
                          Tools.decorate(package.name), Updater.ERROR_TAG)
                log.debug(" git pull returned error: %s", e)

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
