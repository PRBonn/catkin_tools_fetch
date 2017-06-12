"""Contains main for deps verb.

Attributes:
    log (logging.Log): logger
"""

import sys
import logging
from os import path
from argparse import ArgumentParser

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

from catkin_tools_fetch.lib.dependency_parser import Parser
from catkin_tools_fetch.lib.downloader import Downloader
from catkin_tools_fetch.lib.tools import Tools
from catkin_tools_fetch.lib.update import Updater
from catkin_tools_fetch.lib.update import Strategy

logging.basicConfig()
log = logging.getLogger('deps')


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
    config_group.add_argument('--no_status', action='store_true',
                              help='Do not use progress status when cloning.')
    config_group.add_argument('--num_threads', '-j',
                              type=int,
                              default=4,
                              help='Number of threads run in parallel.')

    # Behavior
    behavior_group = parser.add_argument_group(
        'Interface', 'The behavior of the command-line interface.')
    add = behavior_group.add_argument
    add('--verbose', '-v', action='store_true', default=False,
        help='Print output from commands.')

    return parser


def prepare_arguments_deps(parser):
    """Parse arguments that belong to this verb.

    Args:
        parser (argparser): Argument parser

    Returns:
        argparser: Parser that knows about our flags.
    """
    parser.description = """ Manage dependencies for one or more packages in
        a catkin workspace. This reads dependencies from package.xml file of
        each of the packages in the workspace and tries to download their
        sources from version control system of choice."""
    add_context_args(parser)

    parent_parser = ArgumentParser(add_help=False)

    # add config flags to all groups that need it
    parent_parser.add_argument(
        '--default_url', default="{package}",
        help='Where to look for packages by default.')

    # Behavior
    parent_parser.add_argument('--verbose', '-v',
                               action='store_true',
                               default=False,
                               help='Print output from commands.')
    parent_parser.add_argument('--no_status',
                               action='store_true',
                               default=False,
                               help='Do not use progress status when cloning.')
    parent_parser.add_argument('--num_threads', '-j',
                               type=int,
                               default=4,
                               help='Number of threads run in parallel.')

    packages_help_msg = """
        Packages for which the dependencies are analyzed.
        If no packages are given, all packages are processed."""

    # we need subparsers for this verb
    subparsers = parser.add_subparsers(dest='subverb', help="Possible verbs.")

    # add a parser for update sub-verb
    update_help_msg = """
        Update the existing repositories to their latest state from remote."""
    parser_update = subparsers.add_parser(
        'update', help=update_help_msg, parents=[parent_parser])
    config_update_group = parser_update.add_argument_group('Config')
    conflict_help_msg = """ When we pull a git repository there can be
        conflicts. We need to resolve them in some way. You can pick this here.
        By default the plugin will use '%(default)s' strategy."""
    config_update_group.add_argument('--on-conflict', '-r',
                                     choices=Strategy.list_all(),
                                     default=Strategy.IGNORE,
                                     help=conflict_help_msg)

    update_pkg_group = parser_update.add_argument_group(
        'Packages',
        'Control for which packages we update dependencies.')
    update_pkg_group.add_argument('packages',
                                  metavar='PKGNAME',
                                  nargs='*',
                                  help=packages_help_msg)

    # add a parser for fetch sub-verb
    fetch_help_msg = """
        Fetch the dependencies stored package.xml files."""
    parser_fetch = subparsers.add_parser('fetch',
                                         help=fetch_help_msg,
                                         parents=[parent_parser])
    fetch_group = parser_fetch.add_argument_group(
        'Packages',
        'Control for which packages we fetch dependencies.')
    fetch_group.add_argument('packages',
                             metavar='PKGNAME',
                             nargs='*',
                             help=packages_help_msg)

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

    if opts.no_status:
        log.info(" Not printing status messages while cloning.")
        use_preprint = False
    else:
        log.info(" Will print status messages while cloning.")
        use_preprint = True

    log.info(" Using %s threads.", opts.num_threads)

    context = Context.load(opts.workspace, opts.profile, opts, append=True)
    default_url = Tools.prepare_default_url(opts.default_url)
    if not opts.workspace:
        log.critical(" Workspace undefined! Abort!")
        return 1
    if opts.verb == 'fetch' or opts.subverb == 'fetch':
        if opts.verb == 'fetch':
            msg = """
############################# DEPRECATED ###################################
You are using an old deprecated command: `catkin fetch`.
Please use the new command instead:

                `catkin fetch` --> `catkin deps fetch`

It has the same interface. The old command will be removed in future.
############################################################################
            """
            log.warning(msg)
            seconds_to_sleep = 5
            log.info(" Showing deprecation banner for %s seconds.",
                     seconds_to_sleep)
            from time import sleep
            sleep(seconds_to_sleep)
        return fetch(packages=opts.packages,
                     workspace=opts.workspace,
                     context=context,
                     default_url=default_url,
                     use_preprint=use_preprint,
                     num_threads=opts.num_threads)
    if opts.subverb == 'update':
        return update(packages=opts.packages,
                      workspace=opts.workspace,
                      context=context,
                      default_url=default_url,
                      conflict_strategy=opts.on_conflict,
                      use_preprint=use_preprint,
                      num_threads=opts.num_threads)


def update(packages,
           workspace,
           context,
           default_url,
           conflict_strategy,
           use_preprint,
           num_threads):
    """Update packages from the available remotes.

    Args:
        packages (list): A list of packages provided by the user.
        workspace (str): Path to a workspace (without src/ in the end).
        context (Context): Current context. Needed to find current packages.
        default_url (str): A default url with a {package} placeholder in it.
        use_preprint (bool): Show status messages while cloning

    Returns:
        int: Return code. 0 if success. Git error code otherwise.
    """
    ws_path = path.join(workspace, 'src')
    workspace_packages = find_packages(context.source_space_abs,
                                       exclude_subspaces=True,
                                       warnings=[])
    updater = Updater(ws_path=ws_path,
                      packages=workspace_packages,
                      conflict_strategy=conflict_strategy,
                      use_preprint=use_preprint,
                      num_threads=num_threads)
    updater.update_packages(packages)
    return 0


def fetch(packages,
          workspace,
          context,
          default_url,
          use_preprint,
          num_threads):
    """Fetch dependencies of a package.

    Args:
        packages (list): A list of packages provided by the user.
        workspace (str): Path to a workspace (without src/ in the end).
        context (Context): Current context. Needed to find current packages.
        default_url (str): A default url with a {package} placeholder in it.
        use_preprint (bool): Show status messages while cloning

    Returns:
        int: Return code. 0 if success. Git error code otherwise.
    """
    fetch_all = False
    if not packages:
        fetch_all = True

    ws_path = path.join(workspace, 'src')
    ignore_pkgs = Tools.list_all_ros_pkgs()

    already_fetched = set()
    packages = set(packages)

    global_error_code = Downloader.NO_ERROR

    # loop until there are no new dependencies left to download
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
                for new_dep_name in deps_to_fetch.keys():
                    # make sure we don't stop until we analyzed all
                    # dependencies as we have just added these repositories
                    # we must analyze their dependencies too even if we wanted
                    # to download dependencies for one project only.
                    packages.add(new_dep_name)
        try:
            downloader = Downloader(ws_path=ws_path,
                                    available_pkgs=available_pkgs,
                                    ignore_pkgs=ignore_pkgs,
                                    use_preprint=use_preprint,
                                    num_threads=num_threads)
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
