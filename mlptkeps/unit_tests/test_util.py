from unittest import TestCase
from mlptkeps.util import *

class TestUtil(TestCase):
    
    def setUp(self):
        pass
    
    def test_custom_replacement(self):
        self.assertEqual(custom_sanitize('words[bad-words]otherwords',[('bad','good'), ('other', '')]), 'words[good-words]words')
    
    def test_sanitize_html(self):
        self.assertEqual(sanitize_html('<&>"\'/'), '&lt;&amp;&gt;&quot;&#x27;&#x2F;')