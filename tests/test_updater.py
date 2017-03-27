import unittest
import shutil
import tempfile
from os import path
from catkin_tools_fetch.lib.update import Updater
from catkin_tools_fetch.lib.tools import GitBridge


class TestUpdater(unittest.TestCase):
    """Testing the updater."""

    def setUp(self):
        """Create a temporary directory."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Remove the directory after the test."""
        shutil.rmtree(self.test_dir)

    def test_tag_from_output(self):
        """Test getting a tag from a pull output."""
        http_url = "https://github.com/niosus/catkin_tools_fetch"
        output = GitBridge.clone(http_url, self.test_dir)
        output = GitBridge.pull(self.test_dir, "master")
        tag = Updater.tag_from_output(output)
        self.assertEqual(tag, Updater.UP_TO_DATE_TAG)

    def test_merge_fail(self):
        http_url = "https://github.com/niosus/catkin_tools_fetch"
        output = GitBridge.clone(http_url, self.test_dir)
        readme_file = path.join(self.test_dir, "README.md")
        print(readme_file)
        with open(readme_file, 'w'):
            # we rewrite readme file, which causes a conflict on pull
            pass
        output = GitBridge.pull(self.test_dir, "master")
        tag = Updater.tag_from_output(output)
        self.assertEqual(tag, Updater.CONFLICT_TAG)
