"""Module that contains tests for various tools."""
import unittest
from catkin_tools_fetch.lib.tools import Tools
from catkin_tools_fetch.lib.dependency_parser import Dependency


class TestTools(unittest.TestCase):
    """Test various tools that come with the project."""

    def test_prepare_default_urls(self):
        """Test formatting the default dir."""
        urls = [
            "git@path",                     # 0
            "git@path2/",                   # 1
            "https://path",                 # 2
            "https://path2/",               # 3
            "git@some_path.git",            # 4
            "git@some_path/{package}.git",  # 5
            "{package}"                     # 6
        ]
        urls_joined = ','.join(urls)
        prepared_urls = Tools.prepare_default_urls(urls_joined)
        self.assertIn(urls[0] + '/{package}' + '.git', prepared_urls)
        self.assertIn(urls[1] + '{package}' + '.git', prepared_urls)
        self.assertIn(urls[2] + '/{package}', prepared_urls)
        self.assertIn(urls[3] + '{package}', prepared_urls)
        self.assertNotIn(urls[4], prepared_urls)
        self.assertIn(urls[5], prepared_urls)
        self.assertIn(urls[6], prepared_urls)

    def test_populate_urls_with_name(self):
        """Test populating urls with names."""
        urls = ['blah{package}', '{package}', 'blah']
        populated = Tools.populate_urls_with_name(urls=urls, pkg_name='NAME')
        self.assertIn('blahNAME', populated)
        self.assertIn('NAME', populated)
        self.assertNotIn('blah', populated)

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
