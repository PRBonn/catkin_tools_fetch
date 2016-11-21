"""Contains main for deps verb.

Attributes:
    log (logging.Log): logger
"""

import sys
import logging
from os import path

try:
    from catkin_pkg.packages import find_packages
except ImportError as e:
    sys.exit(
        'ImportError: "from catkin_pkg.topological_order import '
        'topological_order" failed: %s\nMake sure that you have installed '
        '"catkin_pkg", and that it is up to date and on the PYTHONPATH.' % e
    )

from catkin_tools.argument_parsing import add_context_args
from catkin_tools.context import Context

from catkin_tools_fetch.fetcher.dependency_parser import Parser
from catkin_tools_fetch.fetcher.downloader import Downloader
from catkin_tools_fetch.fetcher.tools import Tools

logging.basicConfig()
log = logging.getLogger('fetch')


def prepare_arguments(parser):
    """Parse arguments that belong to this verb.

    Args:
        parser (argparser): Argument parser

    Returns:
        argparser: Parser that knows about our flags.
    """
    parser.description = """ Download dependencies for one or more packages in
        a catkin workspace. This reads dependencies from package.xml file of
        each of the packages in the workspace and tries to download their
        sources from version control system of choice."""
    add_context_args(parser)

    packages_help_msg = """
        Packages for which the dependencies are analyzed.
        If no packages are given, all packages are processed."""
    fetch_group = parser.add_argument_group(
        'Packages',
        'Control for which packages we fetch dependencies.')

    fetch_group.add_argument('packages',
                             metavar='PKGNAME',
                             nargs='*',
                             help=packages_help_msg)

    # add config flags to all groups that need it
    config_group = parser.add_argument_group('Config')
    config_group.add_argument(
        '--default_url', default="{package}",
        help='Where to look for packages by default.')
    config_group.add_argument(
        '--update', '-u', action='store_true', default=False,
        help='Update the dependencies to latest version.')

    # Behavior
    behavior_group = parser.add_argument_group(
        'Interface', 'The behavior of the command-line interface.')
    add = behavior_group.add_argument
    add('--verbose', '-v', action='store_true', default=False,
        help='Print output from commands.')

    return parser


def main(opts):
    """Main function for fetch verb.

    Args:
        opts (dict): Options populated by an arg parser.

    Returns:
        int: Return code
    """
    # Load the context
    if opts.verbose:
        log.setLevel(logging.getLevelName("DEBUG"))
        log.debug(" Enabling DEBUG output.")
    else:
        log.setLevel(logging.getLevelName("INFO"))

    context = Context.load(opts.workspace, opts.profile, opts, append=True)
    default_url = Tools.prepare_default_url(opts.default_url)

    if not opts.workspace:
        log.critical(" Workspace undefined! Abort!")
        return 1
    if opts.update:
        log.error(" Sorry, 'update' not implemented yet, but is planned.")
        return 1
    if opts.verb == 'fetch':
        return fetch(packages=opts.packages,
                     workspace=opts.workspace,
                     context=context,
                     default_url=default_url)


def fetch(packages, workspace, context, default_url):
    """Detch dependencies of a package.

    Args:
        packages (list): A list of packages provided by the user.
        workspace (str): Path to a workspace (without src/ in the end).
        context (Context): Current context. Needed to find current packages.
        default_url (str): A default url with a {package} placeholder in it.

    Returns:
        int: Return code. 0 if success. Git error code otherwise.
    """
    fetch_all = False
    if len(packages) == 0:
        fetch_all = True

    ws_path = path.join(workspace, 'src')
    ignore_pkgs = Tools.list_all_ros_pkgs()

    already_fetched = set()

    global_error_code = Downloader.NO_ERROR

    # loop until there are still any new dependencies left to download
    while(True):
        log.info(" Searching for dependencies.")
        deps_to_fetch = {}
        workspace_packages = find_packages(
            context.source_space_abs,
            exclude_subspaces=True, warnings=[])
        available_pkgs = [pkg.name for _, pkg in workspace_packages.items()]
        initial_cloned_pkgs = len(already_fetched)
        for package_path, package in workspace_packages.items():
            if package.name in already_fetched:
                continue
            if fetch_all or (package.name in packages):
                parser = Parser(default_url, package.name)
                package_folder = path.join(ws_path, package_path)
                deps_to_fetch.update(parser.get_dependencies(package_folder))
                already_fetched.add(package.name)
        try:
            downloader = Downloader(ws_path, available_pkgs, ignore_pkgs)
        except ValueError as e:
            log.critical(" Encountered error. Abort.")
            log.critical(" Error message: %s", e.message)
            return 1
        error_code = downloader.download_dependencies(deps_to_fetch)
        if len(already_fetched) == initial_cloned_pkgs:
            log.info(" No new dependencies. Done.")
            break
        if error_code != 0:
            global_error_code = error_code
        log.info(" New packages available. Process their dependencies now.")
    return global_error_code
