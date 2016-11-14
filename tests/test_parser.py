import unittest
from catkin_fetch.fetcher.dependency_parser import Parser


class TestParser(unittest.TestCase):

    def test_init(self):
        parser = Parser("blah_{package}", "name")
        self.assertEqual(Parser.XML_FILE_NAME, "package.xml")
        self.assertTrue("buildtool_depend" in Parser.TAGS)
        self.assertTrue("build_depend" in Parser.TAGS)
        self.assertEqual(parser.pkg_name, "name")

    def test_init_death(self):
        try:
            Parser("blah", "name")
            self.fail()
        except RuntimeError as e:
            expect = '`download_mask` must contain a "{package}" placeholder.'
            self.assertEqual(expect, e.message)
