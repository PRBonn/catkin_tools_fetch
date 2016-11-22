"""Encapsulates a dependency parser.

Attributes:
    log (logging.Log): logger
"""
import os
import logging
from os import path
from xml.dom import minidom

from catkin_tools_fetch.fetcher.tools import Tools

log = logging.getLogger('fetch')


class Parser(object):
    """Parses dependencies of a package.

    Attributes:
        pkg_name (str): Name of currently parsed package.
        TAGS (list): A list of tags that we want to parse.
        URL_TAGS (list): A list of tags to consider when parsing explicit urls.
        XML_FILE_NAME (str): A generic xml name of package to be parsed.
    """

    XML_FILE_NAME = "package.xml"
    TAGS = ["build_depend"]
    URL_TAGS = ["git_url"]

    def __init__(self, download_mask, pkg_name):
        """Initialize a dependency parser.

        Args:
            download_mask (str): a mask containing {package} tag to be replaced
                later, e.g. git@<path>/{package}.git
            pkg_name (str): Name of current package
        """
        super(Parser, self).__init__()
        if '{package}' not in download_mask:
            raise ValueError(
                '`download_mask` must contain a "{package}" placeholder.')
        self.__download_mask = download_mask
        self.pkg_name = pkg_name

    def get_dependencies(self, package_folder):
        """Find and parse package.xml file and return a dict of dependencies.

        Args:
            package_folder (str): A folder to search package.xml in.

        Returns:
            dict: A dictionary with an url for each package name.
        """
        path_to_xml = Parser.__get_package_xml_path(package_folder)
        if not path_to_xml:
            log.critical(" 'package.xml' not found for package [%s].",
                         self.pkg_name)
            return None
        return self.__get_all_dependencies(path_to_xml)

    def __get_all_dependencies(self, path_to_xml):
        """Get a dictionary of all dependencies.

        Args:
            path_to_xml (str): Path to `package.xml` file.

        Returns:
            dict: Dictionary with an url for each dependency name.
        """
        xmldoc = minidom.parse(path_to_xml)
        all_deps = []
        for tag in Parser.TAGS:
            deps = Parser.__node_to_list(xmldoc, tag)
            deps = Parser.__fix_dependencies(deps, self.pkg_name)
            all_deps += deps
        log.info("  %-21s: Found %s dependencies.",
                 Tools.decorate(self.pkg_name),
                 len(all_deps))
        log.debug(" Dependencies: %s", all_deps)
        deps_with_urls = self.__init_dep_dict(all_deps)
        return Parser.__specify_explicit_urls(xmldoc, deps_with_urls)

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

    @staticmethod
    def __specify_explicit_urls(xmldoc, intial_dep_dict):
        """Specify explicit urls instead of default ones.

        Args:
            xmldoc (minidom): Current xml object
            intial_dep_dict (dict): A dict {name: url} with default urls.

        Returns:
            dict: A dict with specific ursl parsed from <export> tags
        """
        dep_dict = dict(intial_dep_dict)
        for url_tag in Parser.URL_TAGS:
            urls_node = xmldoc.getElementsByTagName(url_tag)
            for item in urls_node:
                target = item.attributes['target'].value
                url = item.attributes['url'].value
                dep_dict[target] = url
        return dep_dict

    def __init_dep_dict(self, all_deps_list):
        """Initialize dependency dict with default values.

        Args:
            all_deps_list (str[]): List of all dependencies.

        Returns:
            dict: A dictionary {name: url} with default url for each dependency
        """
        dep_dict = {}
        for dependency in all_deps_list:
            dep_dict[dependency] = self.__download_mask.format(
                package=dependency)
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
