import unittest
from mlptkeps.providers.plaintext_provider import *
from mlptkeps.episodeframework import Episode

class TestPlaintextProvider(unittest.TestCase):
    def test_parse_text(self):
        self.assertEqual(parse_text("""
        01 01 xtsa6 Title can be multiple words
        01 2 x222 Title 2
        3 3 x19da Title 3
        3 4 NonXid1 Title 4
        """), [
            Episode(1, 1, 'xtsa6', title='Title can be multiple words'),
            Episode(1, 2, 'x222', title='Title 2'),
            Episode(3, 3, 'x19da', title='Title 3'),
            Episode(3, 4, 'NonXid1', title='Title 4')
        ])
    def test_parse_text_ignore_comments(self):
        self.assertEqual(parse_text("""
        #IGNORE
        01 01 xtsa6 Title can be multiple words
                           
        01 2 x222 Title 2
        #sdfjksldh
        3 3 x19da Title 3
        """), [
            Episode(1, 1, 'xtsa6', title='Title can be multiple words'),
            Episode(1, 2, 'x222', title='Title 2'),
            Episode(3, 3, 'x19da', title='Title 3')
        ])
