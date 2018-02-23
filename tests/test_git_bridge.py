"""Module for testing the git bridge."""
import unittest
import os
import shutil
import logging
import tempfile
from catkin_tools_fetch.lib.tools import GitBridge
from catkin_tools_fetch.lib.dependency_parser import Dependency

log = logging.getLogger('deps')


class TestGitBridge(unittest.TestCase):
    """Testing the git bridge."""

    def setUp(self):
        """Create a temporary directory."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Remove the directory after the test."""
        shutil.rmtree(self.test_dir)

    def test_status(self):
        """Test that git status gives us branch and status."""
        http_url = "https://github.com/niosus/catkin_tools_fetch"
        name, result = GitBridge.clone("test", http_url, self.test_dir)
        self.assertEqual(name, "test")
        self.assertEqual(result, GitBridge.CLONED_TAG.format(branch="master"))
        output, branch, has_changes = GitBridge.status(self.test_dir)
        expected_output = b"## master...origin/master\n"
        self.assertEqual(output, expected_output)
        self.assertEqual(branch, "master")
        self.assertFalse(has_changes)
        test_file = os.path.join(self.test_dir, "test_file.txt")
        with open(test_file, 'a'):
            output, branch, has_changes = GitBridge.status(self.test_dir)
            expected_output = b"""## master...origin/master
?? test_file.txt
"""
            self.assertEqual(output, expected_output)
            self.assertEqual(branch, "master")
            self.assertTrue(has_changes)

    def test_clone(self):
        """Test if cloning works as expected."""
        wrong_url = "https://github.com/niosus"
        name, result = GitBridge.clone("name", wrong_url, self.test_dir)
        self.assertEqual(name, "name")
        self.assertEqual(result, GitBridge.ERROR_TAG)
        http_url = "https://github.com/niosus/catkin_tools_fetch"
        _, result = GitBridge.clone("", http_url, self.test_dir)
        self.assertEqual(result, GitBridge.CLONED_TAG.format(branch="master"))
        _, result = GitBridge.clone("", http_url, ".")
        self.assertEqual(result, GitBridge.EXISTS_TAG)

    def test_pull(self):
        """Test pulling a repository."""
        http_url = "https://github.com/niosus/catkin_tools_fetch"
        _, output = GitBridge.clone(
            "catkin_tools_fetch", http_url, self.test_dir)
        output = GitBridge.pull(self.test_dir, "master")
        expected_msg = b"""From https://github.com/niosus/catkin_tools_fetch
 * branch            master     -> FETCH_HEAD"""
        self.assertTrue(output.startswith(expected_msg))

    def test_repository_exists(self):
        """Test behavior if repository exists."""
        http_url = "https://github.com/niosus/catkin_tools_fetch"
        dependency = Dependency(name='test', url=http_url)
        dep_res, exists = GitBridge.repository_exists(dependency)
        self.assertTrue(exists)
        self.assertEqual(dep_res.name, dependency.name)

        wrong_url = "https://github.com/niosus"
        dependency = Dependency(name='test', url=wrong_url)
        dep_res, exists = GitBridge.repository_exists(dependency)
        self.assertFalse(exists)
        dependency = Dependency(name='empty', url='')
        dep_res, exists = GitBridge.repository_exists(dependency)
        self.assertFalse(exists)

    def test_get_branch_name(self):
        """Test getting the branch name."""
        test_output = """## master...origin/master
M package.xml
M src/nodes/full_stack.cpp
M src/scripts/CMakeLists.txt
M src/utils/velodyne_utils.cpp
M src/visualization/visualizer.cpp
?? src/scripts/kitti_show_boxes.cpp
"""
        print(test_output)
        branch = GitBridge.get_branch_name(test_output)
        self.assertEqual(branch, "master")
