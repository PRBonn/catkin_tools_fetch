"""Test the updater."""
import unittest
import shutil
import tempfile
from termcolor import colored
from mock import MagicMock, PropertyMock
from catkin_tools_fetch.lib.update import Updater
from catkin_tools_fetch.lib.update import Strategy
from catkin_tools_fetch.lib.tools import GitBridge


def generate_mock_packages(size):
    """Generate a list of mock packages.

    Args:
        size (int): Number of packages to generate.

    Returns:
        mock_list (str[]): list of generated mock packages
        mock_dict (dict{folder, pkg}): dictionary of generated mock packages
    """
    mock_list = []
    mock_dict = {}
    for i in range(size):
        mock_list.append(MagicMock())
        name = "pkg_{}".format(i)
        folder = "folder_{}".format(i)
        type(mock_list[i]).name = PropertyMock(return_value=name)
        mock_dict[folder] = mock_list[i]
    return mock_list, mock_dict


class TestUpdater(unittest.TestCase):
    """Testing the updater."""

    def setUp(self):
        """Create a temporary directory."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Remove the directory after the test."""
        shutil.rmtree(self.test_dir)

    def test_init(self):
        """Test initialization of the updater."""
        ws_path = self.test_dir
        packages = {
            "test_folder": "package_dummy"
        }
        conflict_strategy = "abort"
        updater = Updater(ws_path, packages, conflict_strategy)
        self.assertEquals(ws_path, updater.ws_path)
        self.assertEquals(packages, updater.packages)
        self.assertEquals(conflict_strategy, updater.conflict_strategy)

    def test_filter_packages(self):
        """Test filtering of packages."""
        ws_path = self.test_dir
        mock_list, all_packages = generate_mock_packages(3)
        selected_packages = [mock_list[0].name, mock_list[2].name]
        conflict_strategy = "abort"
        updater = Updater(ws_path, all_packages, conflict_strategy)
        filtered_packages = updater.filter_packages(selected_packages)
        expected_packages = {
            "folder_0": mock_list[0],
            "folder_2": mock_list[2],
        }
        self.assertEquals(expected_packages, filtered_packages)

    def test_filter_packages_none(self):
        """Test filtering of packages when nothing is given."""
        ws_path = self.test_dir
        all_packages = {
            "folder_1": "package_dummy_1",
            "folder_2": "package_dummy_2",
            "folder_3": "package_dummy_3",
        }
        selected_packages = None
        conflict_strategy = "abort"
        updater = Updater(ws_path, all_packages, conflict_strategy)
        filtered_packages = updater.filter_packages(selected_packages)
        self.assertEquals(all_packages, filtered_packages)

    def test_tag_from_output(self):
        """Test getting a tag from a pull output."""
        http_url = "https://github.com/niosus/catkin_tools_fetch"
        _, output = GitBridge.clone(
            "catkin_tools_fetch", http_url, self.test_dir)
        output = GitBridge.pull(self.test_dir, "master")
        tag = Updater.tag_from_output(output)
        self.assertEqual(tag, Updater.UP_TO_DATE_TAG)

    def test_merge_fail(self):
        """Check that we get a correct tag from conflict."""
        output = """CONFLICT (content): Merge conflict in <fileName>
Automatic merge failed; fix conflicts and then commit the result."""
        tag = Updater.tag_from_output(output)
        self.assertEqual(tag, Updater.CONFLICT_TAG)

    def test_merge_success(self):
        """Check that we can parse successful pull output."""
        output = """From github.com:niosus/catkin_tools_fetch
 * branch            master     -> FETCH_HEAD
Already up-to-date.
"""
        tag = Updater.tag_from_output(output)
        self.assertEqual(tag, Updater.UP_TO_DATE_TAG)

    def test_update_full_simple(self):
        """Test updater end to end on single repo."""
        http_url = "https://github.com/niosus/catkin_tools_fetch"
        GitBridge.clone("fetch", http_url, self.test_dir)
        pkg = MagicMock()
        type(pkg).name = PropertyMock(return_value="pkg")
        packages = {
            ".": pkg
        }
        updater = Updater(self.test_dir, packages, "abort")
        selected_packages = [pkg.name]
        status_msgs = updater.update_packages(selected_packages)
        self.assertEquals(len(status_msgs), 1)
        self.assertEquals(status_msgs[0][0], "pkg")
        self.assertEquals(status_msgs[0][1], colored(
            Updater.UP_TO_DATE_TAG, "green"))

    def test_list_strategies(self):
        """Test the list of all strategies."""
        expected = set([Strategy.IGNORE, Strategy.ABORT])
        actual = set(Strategy.list_all())
        self.assertEquals(len(expected.symmetric_difference(actual)), 0)
