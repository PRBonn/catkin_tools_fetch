import unittest
from os import path
from catkin_tools_fetch.fetch.dependency_parser import Parser


class TestParser(unittest.TestCase):

    def test_init(self):
        parser = Parser("blah_{package}", "pkg_name")
        self.assertEqual(Parser.XML_FILE_NAME, "package.xml")
        self.assertTrue("build_depend" in Parser.TAGS)
        self.assertEqual(parser.pkg_name, "pkg_name")

    def test_init_death(self):
        try:
            Parser("blah", "pkg_name")
            self.fail()
        except ValueError as e:
            self.assertTrue(isinstance(e, ValueError))

    def test_get_dependencies(self):
        pkg_folder = path.join(path.dirname(__file__), "data", "simple_pkg")
        parser = Parser("link_default/{package}", "simple_pkg")
        deps = parser.get_dependencies(pkg_folder)
        self.assertIn("dep_1", deps)
        self.assertIn("dep_2", deps)
        self.assertIn("dep_3", deps)

        self.assertEqual(deps["dep_1"], "http_link")
        self.assertEqual(deps["dep_2"], "git_link")
        self.assertEqual(deps["dep_3"], "link_default/dep_3")
