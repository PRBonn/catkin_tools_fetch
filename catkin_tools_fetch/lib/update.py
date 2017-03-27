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
            selected_packages (str[]): List of packages picker by the user.
        """
        log.info(" Pulling packages:")
        packages = self.filter_packages(selected_packages)
        for ws_folder, package in packages.items():
            folder = path.join(self.ws_path, ws_folder)
            output, branch = GitBridge.status(folder)
            # when no changes - output is single line with name of branch
            if output.count('\n') > 1:
                log.info("  %-21s: %s", Tools.decorate(package.name),
                         Updater.CHANGES_TAG)
                continue
            try:
                output = GitBridge.pull(folder, branch)
                if "Already up-to-date" in output:
                    log.info("  %-21s: %s",
                             Tools.decorate(package.name),
                             Updater.UP_TO_DATE_TAG)
                else:
                    log.info("  %-21s: %s",
                             Tools.decorate(package.name), Updater.PULLED_TAG)
            except subprocess.CalledProcessError as e:
                log.error("  %-21s: %s",
                          Tools.decorate(package.name), Updater.ERROR_TAG)
                log.debug(" git pull returned error: %s", e)
