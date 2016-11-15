import unittest
from os import path
from catkin_fetch.fetcher.downloader import Downloader


class TestDownloader(unittest.TestCase):

    def test_init_empty(self):
        ws_path = path.join(path.dirname(__file__), 'data')
        downloader = Downloader(ws_path, [], [])
        self.assertEqual(downloader.ws_path, ws_path)
        self.assertEqual(downloader.available_pkgs, [])
        self.assertEqual(downloader.ignore_pkgs, [])

    def test_init_death(self):
        try:
            Downloader("blah", [], [])
            self.fail()
        except ValueError as e:
            self.assertTrue(isinstance(e, ValueError))

    def test_repository_exists(self):
        http_url = "https://github.com/niosus/catkin_tools_fetch"
        git_url = "git@github.com:niosus/catkin_tools_fetch.git"
        self.assertTrue(Downloader.repository_exists(http_url))
        self.assertTrue(Downloader.repository_exists(git_url))

        wrong_url = "https://github.com/niosus"
        self.assertFalse(Downloader.repository_exists(wrong_url))
