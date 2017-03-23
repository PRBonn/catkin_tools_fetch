import unittest
from catkin_tools_fetch.lib.tools import GitBridge


class TestGitBridge(unittest.TestCase):

    def test_pull(self):
        pass

    def test_status(self):
        http_url = "https://github.com/niosus/catkin_tools_fetch"
        result = GitBridge.clone(http_url, "cloned_path")
        self.assertEqual(result, GitBridge.CLONED_TAG)
        output, branch = GitBridge.status("cloned_path")
        self.assertEqual(branch, "master")

    def test_clone(self):
        wrong_url = "https://github.com/niosus"
        result = GitBridge.clone(wrong_url, "test_path")
        self.assertEqual(result, GitBridge.ERROR_TAG)
        http_url = "https://github.com/niosus/catkin_tools_fetch"
        result = GitBridge.clone(http_url, "test_path")
        self.assertEqual(result, GitBridge.CLONED_TAG)
        result = GitBridge.clone(http_url, ".")
        self.assertEqual(result, GitBridge.EXISTS_TAG)

    def test_repository_exists(self):
        http_url = "https://github.com/niosus/catkin_tools_fetch"
        self.assertTrue(GitBridge.repository_exists(http_url))

        wrong_url = "https://github.com/niosus"
        self.assertFalse(GitBridge.repository_exists(wrong_url))
        self.assertFalse(GitBridge.repository_exists(""))

    def test_get_branch_name(self):
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
    pass
