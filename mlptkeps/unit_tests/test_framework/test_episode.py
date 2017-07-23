import unittest
from mlptkeps.episodeframework import *
from . import *

class TestEpisode(unittest.TestCase):
    
    def test_episode_equality(self):
        self.assertEqual(Episode(2,3,'xwhataniceid',title='This is a demo video',status=1),Episode(2,3,'xwhataniceid',title='This is a demo video'))
        
    def test_episode_to_string(self):
        self.assertEqual(Episode(2,3,'x123456',title='Example Title').__str__(), 's2ep3 - \'Example Title\'')
        
    def test_episode_repr(self):
        self.assertEqual(Episode(2,3,'xmLPfIm',title='Example Title').__repr__(), 's2ep3 - \'Example Title\' (xmLPfIm)')
    
    def test_episode_less_than(self):
        eps = [Episode(s,ep,'id') for s in range(1,3) for ep in range(1,3)]
        results = [ep1 < ep2 for ep1 in eps for ep2 in eps]
        self.assertListEqual(results,[
            False, True,  True,  True,
            False, False, True,  True,
            False, False, False, True,
            False, False, False, False
        ])
    
    def test_episode_greater_than(self):
        eps = [Episode(s,ep,'id') for s in range(1,3) for ep in range(1,3)]
        results = [ep1 > ep2 for ep1 in eps for ep2 in eps]
        self.assertListEqual(results,[
            False, False, False, False,
            True,  False, False, False,
            True,  True,  False, False,
            True,  True,  True,  False
        ])
    
    def test_episode_less_equal(self):
        eps = [Episode(s,ep,'id') for s in range(1,3) for ep in range(1,3)]
        results = [ep1 <= ep2 for ep1 in eps for ep2 in eps]
        self.assertListEqual(results,[
            True,  True,  True,  True,
            False, True,  True,  True,
            False, False, True,  True,
            False, False, False, True
        ])
    
    def test_episode_greater_equal(self):
        eps = [Episode(s,ep,'id') for s in range(1,3) for ep in range(1,3)]
        results = [ep1 >= ep2 for ep1 in eps for ep2 in eps]
        self.assertListEqual(results,[
            True,  False, False, False,
            True,  True,  False, False,
            True,  True,  True,  False,
            True,  True,  True,  True
        ])
    
    def test_episode_not_equal(self):
        eps = [Episode(s,ep,'id') for s in range(1,3) for ep in range(1,3)]
        results = [ep1 != ep2 for ep1 in eps for ep2 in eps]
        self.assertListEqual(results,[
            False, True,  True,  True,
            True,  False, True,  True,
            True,  True,  False, True,
            True,  True,  True,  False
        ])
    
    def test_episode_int(self):
        eps = [int(Episode(s,ep,'id')) for s in range(1,3) for ep in range(1,3)]
        self.assertListEqual(eps,[101, 102, 201, 202])
    
    def test_episode_reject_non_alphanumeric_ids(self):
        bad_hombres = '<>&"/\''
        for char in bad_hombres:
            self.assertRaises(ValueError,Episode,1,1,char)