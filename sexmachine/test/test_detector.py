# -*- coding: utf-8 -*-
import unittest
import sexmachine.detector as d

class TestDetector(unittest.TestCase):

    def setUp(self):
        self.case = d.Detector()

    def test_gender(self):
        self.assertEqual(self.case.get_gender("Bob"), "M")
        self.assertEqual(self.case.get_gender("Sally"), "F")
        self.assertEqual(self.case.get_gender("Pauley"), "A")

    def test_unicode(self):
        self.assertEqual(self.case.get_gender("Álfrún"), "F")
        self.assertEqual(self.case.get_gender("Ayşe"), "F")
        self.assertEqual(self.case.get_gender("Gavriliţă"), "F")
        self.assertEqual(self.case.get_gender("İsmet"), "M")
        self.assertEqual(self.case.get_gender("Snæbjörn"), "M")

    def test_country(self):
        self.assertEqual(self.case.get_gender("Jamie"), "MF")
        self.assertEqual(self.case.get_gender("Jamie", "great_britain"), "MM")
        self.assertEqual(self.case.get_gender("Jamie", "Great Britain"), "MM")

if __name__ == '__main__':
    unittest.main()
