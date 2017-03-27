"""Summary."""
import re
import logging
import subprocess
from os import path

from catkin_tools_fetch.common.tools import Tools

log = logging.getLogger('fetch')


GIT_STATUS_CMD = "git status --porcelain --branch"
GIT_PULL_CMD_MASK = "git pull origin {branch}"

GIT_UP_TO_DATE_MSG = "Already up-to-date"
GIT_MERGE_FAILED_MSG = "Automatic merge failed"
GIT_CLEAN_MSG = "working directory clean"

BRANCH_REGEX = re.compile("## (?!HEAD)([\w\-_]+)")

CHANGES_TAG = "[UNCOMMITTED CHANGES]"
NO_TRACK_TAG = "[NO BRANCH]"
UP_TO_DATE_TAG = "[UP TO DATE]"
PULLED_TAG = "[PULLED]"
ERROR_TAG = "[GIT ERROR]"
CONFLICT_TAG = "[MERGE CONFLICT]"

OK_TAGS = [PULLED_TAG, UP_TO_DATE_TAG]


def update_folders(ws_path, packages, conflict_strategy):
    """Go through all folders and update them from git.

    Args:
        folders (dict): Packages in a workspace.
        conflict_strategy (str): The way we handle conflicts.

    Returns:
        TYPE: Description
    """
    log.info(" Pulling packages:")
    for ws_folder, package in packages.items():
        folder = path.join(ws_path, ws_folder)
        output = subprocess.check_output(GIT_STATUS_CMD,
                                         stderr=subprocess.STDOUT,
                                         shell=True,
                                         cwd=folder)
        # when no changes - output is single line with name of branch
        if output.count('\n') > 1:
            log.info("  %-21s: %s", Tools.decorate(package.name), CHANGES_TAG)
            continue
        match = BRANCH_REGEX.match(output)
        if not match:
            log.info("  %-21s: %s", Tools.decorate(package.name), NO_TRACK_TAG)
            continue
        branch = match.groups()[0]
        git_pull_cmd = GIT_PULL_CMD_MASK.format(branch=branch)
        try:
            output = subprocess.check_output(git_pull_cmd,
                                             stderr=subprocess.STDOUT,
                                             shell=True,
                                             cwd=folder)
            status_tag = get_status_tag(output)
            log_func = log.info
            if status_tag not in OK_TAGS:
                log_func = log.warning
            log_func(Tools.decorate(package.name), status_tag)
        except subprocess.CalledProcessError as e:
            log.error("  %-21s: %s", Tools.decorate(package.name), ERROR_TAG)
            log.debug(" git pull returned error: %s", e)


def get_status_tag(output):
    """Get status from git command output."""
    if GIT_UP_TO_DATE_MSG in output:
        return UP_TO_DATE_TAG
    if GIT_MERGE_FAILED_MSG in output:
        return CONFLICT_TAG
    return PULLED_TAG
