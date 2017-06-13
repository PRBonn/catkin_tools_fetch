"""Module that contains tests for various tools."""
import unittest
from catkin_tools_fetch.lib.tools import Tools
from catkin_tools_fetch.lib.dependency_parser import Dependency


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

    def test_update_deps(self):
        """Test that we can update the dictionary."""
        old_dict = {'test': Dependency(name='test')}
        new_dict = {
            'test2': Dependency(name='test2'),
            'test': Dependency(name='test', branch='blah')
        }
        updated_dict = Tools.update_deps_dict(old_dict, new_dict)
        self.assertTrue('test' in updated_dict)
        self.assertTrue('test2' in updated_dict)
        self.assertEqual('blah', updated_dict['test'].branch)
        pass
