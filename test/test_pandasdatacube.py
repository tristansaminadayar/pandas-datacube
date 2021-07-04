import unittest

from pandasdatacube.pandasdatacube import *


class Tests(unittest.TestCase):
    def test_expand_name(self):
        expand_dict: dict = {'dbnary': 'http://kaiko.getalp.org/dbnary#',
                             'dbnstats': 'http://kaiko.getalp.org/dbnary/statistics/',
                             'lime': 'http://www.w3.org/ns/lemon/lime#'}
        self.assertEqual(expand_name('dbnstats:dbnaryNymRelationsCube', expand_dict),
                         'http://kaiko.getalp.org/dbnary/statistics/dbnaryNymRelationsCube')

        self.assertEqual(expand_name('dbnary:wiktionaryDumpVersion', expand_dict),
                         'http://kaiko.getalp.org/dbnary#wiktionaryDumpVersion')

        self.assertEqual(expand_name('lime:language', expand_dict),
                         'http://www.w3.org/ns/lemon/lime#language')

        self.assertRaises(KeyError, expand_name, 'owl:language', expand_dict)

        self.assertRaises(ValueError, expand_name, 'owl:lime:language', expand_dict)


if __name__ == '__main__':
    unittest.main()
