"""Test downloading of the dependencies."""
import unittest
import tempfile
import shutil
from os import path
from catkin_tools_fetch.lib.downloader import Downloader
from catkin_tools_fetch.lib.dependency_parser import Dependency


class TestDownloader(unittest.TestCase):
    """Test downloader class."""

    def setUp(self):
        """Create a temporary directory."""
        self.test_dir = tempfile.mkdtemp("_ws", "temp_")

    def tearDown(self):
        """Remove the directory after the test."""
        shutil.rmtree(self.test_dir)

    def test_init_empty(self):
        """Test that initialization is empty."""
        ws_path = path.join(path.dirname(__file__), 'data')
        downloader = Downloader(ws_path, [], [])
        self.assertEqual(downloader.ws_path, ws_path)
        self.assertEqual(downloader.available_pkgs, [])
        self.assertEqual(downloader.ignore_pkgs, [])

    def test_download_dependencies_simple(self):
        """Test simple dependencies downloader."""
        downloader = Downloader(self.test_dir, [], [])
        dependency = Dependency(
            name="fetch",
            url="https://github.com/niosus/catkin_tools_fetch")
        dep_dict = {"fetch": dependency}
        downloader.download_dependencies(dep_dict)
        expected_path = path.join(self.test_dir,
                                  'fetch',
                                  'README.md')
        self.assertTrue(path.exists(expected_path))

    def test_download_dependencies_again(self):
        """Test that downloading them again breaks nothing."""
        downloader = Downloader(self.test_dir, [], [])
        dependency = Dependency(
            name="fetch",
            url="https://github.com/niosus/catkin_tools_fetch")
        dep_dict = {"fetch": dependency}
        downloader.download_dependencies(dep_dict)
        downloader.download_dependencies(dep_dict)
        expected_path = path.join(self.test_dir,
                                  'fetch',
                                  'README.md')
        self.assertTrue(path.exists(expected_path))

    def test_no_download_for_ros_deps(self):
        """Test that we skip ROS packages."""
        downloader = Downloader(self.test_dir, [], [])
        roscpp_dep = Dependency(name="roscpp", url="irrelevant_link")
        std_msgs_dep = Dependency(name="std_msgs", url="irrelevant_link")
        dep_dict = {"roscpp": roscpp_dep, "std_msgs": std_msgs_dep}
        downloader.download_dependencies(dep_dict)
        expected_path = path.join(self.test_dir, 'roscpp')
        self.assertFalse(path.exists(expected_path))
        expected_path = path.join(self.test_dir, 'std_msgs')
        self.assertFalse(path.exists(expected_path))

    def test_no_download_for_wrong_link(self):
        """Test that we download nothing for a wrong link."""
        downloader = Downloader(self.test_dir, [], [])
        dependency = Dependency(name="fetch", url="wrong_link")
        dep_dict = {"fetch": dependency}
        downloader.download_dependencies(dep_dict)
        expected_path = path.join(self.test_dir, 'fetch')
        self.assertFalse(path.exists(expected_path))

    def test_no_download_for_wrong_branch(self):
        """Test that we download nothing for a wrong branch."""
        downloader = Downloader(self.test_dir, [], [])
        dependency = Dependency(
            name="fetch",
            url="https://github.com/niosus/catkin_tools_fetch",
            branch="blahblah")
        dep_dict = {"fetch": dependency}
        downloader.download_dependencies(dep_dict)
        expected_path = path.join(self.test_dir, 'fetch')
        self.assertFalse(path.exists(expected_path))

    def test_init_death(self):
        """Test death when init is wrong."""
        try:
            Downloader("blah", [], [])
            self.fail()
        except ValueError as e:
            self.assertTrue(isinstance(e, ValueError))

    def test_download_dependencies_death(self):
        """Test that we throw an exception for wrong input dict."""
        downloader = Downloader(self.test_dir, [], [])
        not_a_dict = {"not", "a dictionary"}
        self.assertRaises(ValueError,
                          downloader.download_dependencies,
                          not_a_dict)
