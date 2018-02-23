"""Encapsulates a dependency parser.

Attributes:
    log (logging.Log): logger
"""
import os
import logging
from os import path
from xml.dom import minidom

from catkin_tools_fetch.lib.tools import Tools
from catkin_tools_fetch.lib.printer import Printer

log = logging.getLogger('deps')


class Dependency(object):
    """Incapsulate a single dependency here."""

    def __init__(self, name, url=None, branch=None):
        """Initialize a dependency.

        Args:
            name (str): Name of the dependee package
            url (str): Explicit location url
            branch (str): Name of branch
        """
        self.name = name
        self.url = url
        self.branch = branch
        self.default_urls = set()

    def set_default_urls_if_needed(self, default_urls):
        """Set default urls if no url set before."""
        if not default_urls:
            return
        if self.url:
            log.info(
                " Package [%s]: Skip default urls. Explicit one defined: %s",
                self.name, self.url)
            return
        self.default_urls = Tools.populate_urls_with_name(urls=default_urls,
                                                          pkg_name=self.name)

    def __repr__(self):
        """Show how to print it."""
        return "name: '{}', branch: '{}', url: '{}'".format(
            self.name, self.branch, self.url)


class Parser(object):
    """Parses dependencies of a package.

    Attributes:
        pkg_name (str): Name of currently parsed package.
        TAGS (list): A list of tags that we want to parse.
        URL_TAGS (list): A list of tags to consider when parsing explicit urls.
        XML_FILE_NAME (str): A generic xml name of package to be parsed.
    """

    XML_FILE_NAME = "package.xml"
    TAGS = ["build_depend", "depend"]
    URL_TAGS = ["git_url"]

    def __init__(self, default_urls, pkg_name):
        """Initialize a dependency parser.

        Args:
            default_urls (set(str)): a set of masks containing {package}
                tag to be replaced later, e.g. git@<path>/{package}.git
            pkg_name (str): Name of current package
        """
        super(Parser, self).__init__()
        # First perform a sanity check.
        for url in default_urls:
            if '{package}' not in url:
                error = "Default url: '{}' must contain: '{}'".format(
                    url, Tools.PACKAGE_TAG)
                raise ValueError(error)
        self.default_urls = default_urls
        self.pkg_name = pkg_name
        self.printer = Printer()

    def get_dependencies(self, package_folder):
        """Find and parse package.xml file and return a dict of dependencies.

        Args:
            package_folder (str): A folder to search package.xml in.

        Returns:
            dict: A dictionary with a dependency for each package name.
        """
        path_to_xml = Parser.__get_package_xml_path(package_folder)
        if not path_to_xml:
            log.critical(" 'package.xml' not found for package [%s].",
                         self.pkg_name)
            return None
        xmldoc = minidom.parse(path_to_xml)
        all_deps = []
        for tag in Parser.TAGS:
            deps = Parser.__node_to_list(xmldoc, tag)
            deps = Parser.__fix_dependencies(deps, self.pkg_name)
            all_deps += deps
        msg = " {}: Found {} valid dependencies".format(
            Tools.decorate(self.pkg_name), len(all_deps))
        self.printer.print_msg(msg)
        log.debug(" Dependencies: %s", all_deps)
        deps_with_urls = self.__init_dep_dict(all_deps)
        return self.__update_explicit_values(xmldoc, deps_with_urls)

    @staticmethod
    def __fix_dependencies(deps, pkg_name):
        """Fix dependencies if they are malformed.

        Args:
            deps (str[]): List of dependencies.
            pkg_name (str): Current package name.

        Returns:
            str[]: Fixed dependencies.
        """
        fixed_deps = list(deps)
        for i, dep in enumerate(deps):
            fixed_deps[i] = dep.strip()
            if fixed_deps[i] != dep:
                log.warning(
                    " [%s]: Fix dependency in `package.xml`: [%s] to [%s]",
                    pkg_name, dep, fixed_deps[i])
        return fixed_deps

    def __update_explicit_values(self, xmldoc, dep_dict):
        """Specify explicit values instead of default ones.

        A user can define explicit values for each package in the <export> tag.
        Values to be specified: url, branch.

        This function reads the appropriate part of `package.xml` file and
        replaces the default values with the ones it finds there.

        Args:
            xmldoc (minidom): Current xml object
            dep_dict (dict): A dict {name: dep} with default deps.

        Returns:
            dict: A dict with final dependencies parsed from <export> tags
        """
        for url_tag in Parser.URL_TAGS:
            urls_node = xmldoc.getElementsByTagName(url_tag)
            for item in urls_node:
                target = Parser.__get_attr('target', item)
                if not target:
                    log.warning(" skip xml item: '%s'", item)
                    continue
                log.debug(" read target:'%s'", target)
                url = Parser.__get_attr('url', item)
                if url:
                    if target == 'all':
                        # The target is 'all' so this denotes a default url.
                        prepared_url = Tools.prepare_default_url(url)
                        if prepared_url:
                            self.default_urls.add(prepared_url)
                        else:
                            log.error("Url: '%s' is wrongly formatted.", url)
                        # We are done reading this entry, skip to next now.
                        continue
                    # Here we assume url is a full explicit url to package.
                    dep_dict[target].url = url
                    log.debug(" target url:'%s'", url)
                branch = Parser.__get_attr('branch', item)
                if branch:
                    dep_dict[target].branch = branch
                    log.debug(" target branch:'%s'", branch)
                log.debug(" updated dependency: %s", dep_dict[target])
        # Update the default urls for all dependencies
        for dep in dep_dict.values():
            dep.set_default_urls_if_needed(self.default_urls)
        return dep_dict

    @staticmethod
    def __get_attr(attr_name, xml_item):
        """Get attribute from xml item if possible."""
        attr = None
        try:
            attr = xml_item.attributes[attr_name].value
        except KeyError:
            log.debug(" '%s' not found in xml item '%s'.", attr_name, xml_item)
        return attr

    def __init_dep_dict(self, all_deps_list):
        """Initialize dependency dict with default values.

        Args:
            all_deps_list (str[]): List of all dependencies.

        Returns:
            dict: A dictionary {name: dep} with dependency objects
        """
        dep_dict = {}
        for dep_name in all_deps_list:
            dependency = Dependency(name=dep_name)
            dep_dict[dep_name] = dependency
        return dep_dict

    @staticmethod
    def __node_to_list(xmldoc, xml_node_name):
        """Get list of elements for a name of node.

        Args:
            xmldoc (minidom): Object for xml file.
            xml_node_name (str): Node name.

        Returns:
            str[]: List of all names in node
        """
        node = xmldoc.getElementsByTagName(xml_node_name)
        return [str(s.childNodes[0].nodeValue) for s in node]

    @staticmethod
    def __get_package_xml_path(folder):
        """Get path of `package.xml` file in folder.

        Args:
            folder (str): Folder to search file in.

        Returns:
            str: Full path to file or None if not found.
        """
        for file in os.listdir(folder):
            if file == Parser.XML_FILE_NAME:
                full_path = path.join(folder, file)
                return full_path
        return None
