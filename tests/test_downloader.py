import unittest
import tempfile
from os import path
from catkin_fetch.fetcher.downloader import Downloader


class TestDownloader(unittest.TestCase):

    def test_init_empty(self):
        ws_path = path.join(path.dirname(__file__), 'data')
        downloader = Downloader(ws_path, [], [])
        self.assertEqual(downloader.ws_path, ws_path)
        self.assertEqual(downloader.available_pkgs, [])
        self.assertEqual(downloader.ignore_pkgs, [])

    def test_repository_exists(self):
        http_url = "https://github.com/niosus/catkin_tools_fetch"
        git_url = "git@github.com:niosus/catkin_tools_fetch.git"
        self.assertTrue(Downloader.repository_exists(http_url))
        self.assertTrue(Downloader.repository_exists(git_url))

        wrong_url = "https://github.com/niosus"
        self.assertFalse(Downloader.repository_exists(wrong_url))
        self.assertFalse(Downloader.repository_exists(""))

    def test_download_dependencies_simple(self):
        temp_dir = tempfile.mkdtemp("_ws", "temp_")
        downloader = Downloader(temp_dir, [], [])
        dep_dict = {"fetch": "https://github.com/niosus/catkin_tools_fetch"}
        downloader.download_dependencies(dep_dict)
        expected_path = path.join(temp_dir,
                                  'fetch',
                                  'README.md')
        self.assertTrue(path.exists(expected_path))

    def test_no_download_for_ros_deps(self):
        temp_dir = tempfile.mkdtemp("_ws", "no_ros_")
        downloader = Downloader(temp_dir, [], [])
        dep_dict = {
            "roscpp": "irrelevant_link",
            "std_msgs": "irrelevant_link"}
        downloader.download_dependencies(dep_dict)
        expected_path = path.join(temp_dir, 'roscpp')
        self.assertFalse(path.exists(expected_path))
        expected_path = path.join(temp_dir, 'std_msgs')
        self.assertFalse(path.exists(expected_path))

    def test_no_download_for_wrong_link(self):
        temp_dir = tempfile.mkdtemp("_ws", "no_ros_")
        downloader = Downloader(temp_dir, [], [])
        dep_dict = {"fetch": "wrong_link"}
        downloader.download_dependencies(dep_dict)
        expected_path = path.join(temp_dir, 'fetch')
        self.assertFalse(path.exists(expected_path))

    def test_init_death(self):
        try:
            Downloader("blah", [], [])
            self.fail()
        except ValueError as e:
            self.assertTrue(isinstance(e, ValueError))

    def test_download_dependencies_death(self):
        temp_dir = tempfile.mkdtemp("_ws", "temp_")
        downloader = Downloader(temp_dir, [], [])
        not_a_dict = {"not", "a dictionary"}
        self.assertRaises(ValueError,
                          downloader.download_dependencies,
                          not_a_dict)
