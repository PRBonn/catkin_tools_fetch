"""Module that contains tests for various tools."""
import unittest
from catkin_tools_fetch.lib.tools import Tools


class TestTools(unittest.TestCase):
    """Test various tools that come with the project."""

    def test_prepare_default_url(self):
        """Test formatting the default dir."""
        test_url = ''
        self.assertEqual(test_url, Tools.prepare_default_url(test_url))
        test_url_git = 'git@path/'
        self.assertEqual(test_url_git + '{package}' + '.git',
                         Tools.prepare_default_url(test_url_git))
        test_url_git = 'git@path'
        self.assertEqual(test_url_git + '/{package}' + '.git',
                         Tools.prepare_default_url(test_url_git))
        test_url_http = 'https://path/'
        self.assertEqual(test_url_http + '{package}',
                         Tools.prepare_default_url(test_url_http))
        test_url_http = 'https://path'
        self.assertEqual(test_url_http + '/{package}',
                         Tools.prepare_default_url(test_url_http))

    def test_decorate(self):
        """Test how we decorate something."""
        self.assertEqual('[blah]'.ljust(25), Tools.decorate('blah'))

    def test_default_ros_pkgs(self):
        """Test that we actually remove the default ros packages from list."""
        pkgs = Tools.list_all_ros_pkgs()
        diff = pkgs.symmetric_difference(Tools.default_ros_packages)
        print(diff)
        self.assertTrue(len(diff) < 100)
