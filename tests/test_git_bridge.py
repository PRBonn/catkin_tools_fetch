import unittest
import shutil
import tempfile
from catkin_tools_fetch.lib.tools import GitBridge


class TestGitBridge(unittest.TestCase):
    """Testing the git bridge."""

    def setUp(self):
        """Create a temporary directory."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Remove the directory after the test."""
        shutil.rmtree(self.test_dir)

    def test_pull(self):
        """Test pulling a repository."""
        pass

    def test_status(self):
        """Test that git status gives us branch and status."""
        http_url = "https://github.com/niosus/catkin_tools_fetch"
        result = GitBridge.clone(http_url, self.test_dir)
        self.assertEqual(result, GitBridge.CLONED_TAG)
        _, branch = GitBridge.status(self.test_dir)
        self.assertEqual(branch, "master")

    def test_clone(self):
        """Test if cloning works as expected."""
        wrong_url = "https://github.com/niosus"
        result = GitBridge.clone(wrong_url, self.test_dir)
        self.assertEqual(result, GitBridge.ERROR_TAG)
        http_url = "https://github.com/niosus/catkin_tools_fetch"
        result = GitBridge.clone(http_url, self.test_dir)
        self.assertEqual(result, GitBridge.CLONED_TAG)
        result = GitBridge.clone(http_url, ".")
        self.assertEqual(result, GitBridge.EXISTS_TAG)

    def test_repository_exists(self):
        """Test behavior if repository exists."""
        http_url = "https://github.com/niosus/catkin_tools_fetch"
        self.assertTrue(GitBridge.repository_exists(http_url))

        wrong_url = "https://github.com/niosus"
        self.assertFalse(GitBridge.repository_exists(wrong_url))
        self.assertFalse(GitBridge.repository_exists(""))

    def test_get_branch_name(self):
        """Test getting the branch name."""
        test_output = """## master...origin/master
            M package.xml
            M src/nodes/full_stack.cpp
            M src/scripts/CMakeLists.txt
            M src/utils/velodyne_utils.cpp
            M src/visualization/visualizer.cpp
            ?? src/scripts/kitti_show_boxes.cpp"""
        print(test_output)
        branch = GitBridge.get_branch_name(test_output)
        self.assertEqual(branch, "master")
