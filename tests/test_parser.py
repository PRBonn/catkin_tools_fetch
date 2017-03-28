"""Module to test the parser and dependencies."""
import unittest
from os import path
from catkin_tools_fetch.lib.dependency_parser import Parser
from catkin_tools_fetch.lib.dependency_parser import Dependency


class TestParser(unittest.TestCase):
    """Testing the dependency parser."""

    def test_init(self):
        """Initialize the parser."""
        parser = Parser("blah_{package}", "pkg_name")
        self.assertEqual(Parser.XML_FILE_NAME, "package.xml")
        self.assertTrue("build_depend" in Parser.TAGS)
        self.assertEqual(parser.pkg_name, "pkg_name")

    def test_init_death(self):
        """Test that wrong initialization fails."""
        try:
            Parser("blah", "pkg_name")
            self.fail()
        except ValueError as e:
            self.assertTrue(isinstance(e, ValueError))

    def test_get_dependencies(self):
        """Test that parsing dependencies works."""
        pkg_folder = path.join(path.dirname(__file__), "data", "simple_pkg")
        parser = Parser("link_default/{package}", "simple_pkg")
        deps = parser.get_dependencies(pkg_folder)
        self.assertIn("dep_1", deps)
        self.assertIn("dep_2", deps)
        self.assertIn("dep_3", deps)

        self.assertEqual(deps["dep_1"].name, "dep_1")
        self.assertEqual(deps["dep_1"].url, "http_link")
        self.assertIsNone(deps["dep_1"].branch)

        self.assertEqual(deps["dep_2"].name, "dep_2")
        self.assertEqual(deps["dep_2"].url, "git_link")
        self.assertEqual(deps["dep_2"].branch, "dev")

        self.assertEqual(deps["dep_3"].name, "dep_3")
        self.assertEqual(deps["dep_3"].url, "link_default/dep_3")
        self.assertIsNone(deps["dep_3"].branch)


class TestDependency(unittest.TestCase):
    """Testing the dependency class."""

    def test_init(self):
        """Test initialization."""
        dep = Dependency(name="dep", url="url", branch="master")
        self.assertEquals(dep.name, "dep")
        self.assertEquals(dep.url, "url")
        self.assertEquals(dep.branch, "master")

    def test_init_partial(self):
        """Test partial initialization."""
        dep = Dependency(name="dep")
        self.assertEquals(dep.name, "dep")
        self.assertIsNone(dep.url)
        self.assertIsNone(dep.branch)
