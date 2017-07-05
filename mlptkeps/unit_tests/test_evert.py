import responses
import unittest
from mlptkeps.providers.evert import *
from mlptkeps import episodeframework
import sys

class TestEvert(unittest.TestCase):
    
    example_resp = """
console.log('%cStop!', "font-size:35px;color:red;")
console.log('%cHello, curious little foal c;', "font-size:25px;color:green;")

/* ALL EPISODES */
var episodes = [
  [
    {
      "title": "Episode Title #1",
      "dailymotion": "//www.dailymotion.com/video/x3syjbp",
      "available": true
    },
    {
      "title": "Episode Title #2",
      "dailymotion": "http://www.dailymotion.com/video/xv3o78",
      "available": true
    }
  ],
  [
    {
      "title": "Season 2 Premier",
      "dailymotion": "https://www.dailymotion.com/video/x3nferb-long-video-title",
      "available": true
    },
    {
      "title": "Season 2 Finale",
      "dailymotion": "www.dailymotion.com/video/x2drdtm-long-video-title",
      "available": true
    }
  ]
];
/* Utility functions */
function RLS_episode(season, episode) {
	if(episodes[season-1] == null) {
		return {error: "Invalid season!"};
	}
	if(episodes[season-1][episode-1]) {
		return episodes[season-1][episode-1];
	}
}
"""
    
    def setUp(self):
        self.evr = Evert()
         
    def test_get_batch(self):
        with responses.RequestsMock() as rm:
            rm.add(responses.GET, 'https://mlp-episodes.tk/js/episodes.js', body=TestEvert.example_resp)
            assert len(self.evr.get_batch()) == 4
        
    def test_batch_season_and_episode_numbers(self):
        with responses.RequestsMock() as rm:
            rm.add(responses.GET, 'https://mlp-episodes.tk/js/episodes.js', body=TestEvert.example_resp)
            bat = self.evr.get_batch()
            assert bat[0].season == 1
            assert bat[0].episode == 1
            assert bat[1].season == 1
            assert bat[1].episode == 2
            assert bat[2].season == 2
            assert bat[2].episode == 1
            assert bat[3].season == 2
            assert bat[3].episode == 2
        
    def test_batch_titles(self):
        with responses.RequestsMock() as rm:
            rm.add(responses.GET, 'https://mlp-episodes.tk/js/episodes.js', body=TestEvert.example_resp)
            bat = self.evr.get_batch()
            titles = list(map(lambda ep: ep.title, bat))
            self.assertEqual(titles, ['Episode Title #1', 'Episode Title #2', 'Season 2 Premier','Season 2 Finale'])
        
    def test_batch_dailymotion_ids(self):
        with responses.RequestsMock() as rm:
            rm.add(responses.GET, 'https://mlp-episodes.tk/js/episodes.js', body=TestEvert.example_resp)
            bat = self.evr.get_batch()
            ids = list(map(lambda ep: ep.dailymotion_id, bat))
            self.assertEqual(ids, ['x3syjbp','xv3o78','x3nferb','x2drdtm'])
        
    def test_batch_full(self):
        with responses.RequestsMock() as rm:
            rm.add(responses.GET, 'https://mlp-episodes.tk/js/episodes.js', body=TestEvert.example_resp)
            self.assertEqual(self.evr.get_batch(),[
                episodeframework.Episode(1,1,'x3syjbp',title='Episode Title #1'),
                episodeframework.Episode(1,2,'xv3o78',title='Episode Title #2'),
                episodeframework.Episode(2,1,'x3nferb',title='Season 2 Premier'),
                episodeframework.Episode(2,2,'x2drdtm',title='Season 2 Finale')
            ])

if __name__ == '__main__':
    unittest.main()