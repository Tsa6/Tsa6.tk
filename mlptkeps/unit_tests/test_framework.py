import responses
import unittest
from unittest import mock
from mlptkeps.episodeframework import *

class TestFramework(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_episode_equality(self):
        self.assertEqual(Episode(2,3,'xwhataniceid',title='This is a demo video',status=1),Episode(2,3,'xwhataniceid',title='This is a demo video'))
        
    def test_episode_to_string(self):
        self.assertEqual(Episode(2,3,'x123456',title='Example Title').__str__(), 's2ep3 - \'Example Title\'')
    
    def test_episode_reject_non_alphanumeric_ids(self):
        bad_hombres = '<>&"/\''
        for char in bad_hombres:
            self.assertRaises(ValueError,Episode,1,1,char)
    
    def test_proc_batch(self):
        with responses.RequestsMock() as rm:
            rm.add(responses.GET,'https://api.dailymotion.com/videos?fields=id&ids=x123456,xabcdef&limit=100&page=1',json={
                "page":1,
                "limit":100,
                "explicit":False,
                "total":2,
                "has_more":False,
                "list":[{"id":"xabcdef"}]
            }, match_querystring=True)
            bat = [
                Episode(1,2,'x123456'),
                Episode(8,3,'xabcdef')
            ]
            proc_batch(bat)
            self.assertEqual([bat[0].status, bat[1].status], [0,1])
        
    def test_proc_batch_multi_page(self):
        with responses.RequestsMock() as rm:
            rm.add(responses.GET,'https://api.dailymotion.com/videos?fields=id&ids=x123456,xabcdef,xabddef,xabeef,xabccdef,x12ef,xab44cdef,xabcddef&limit=100&page=1',json={
                "page":1,
                "limit":5,
                "explicit":False,
                "total":5,
                "has_more":True,
                "list":[{"id":"x123456"},{"id":"xabddef"},{"id":"xabeef"},{"id":"xabccdef"},{"id":"x12ef"}]
            }, match_querystring=True)
            rm.add(responses.GET,'https://api.dailymotion.com/videos?fields=id&ids=x123456,xabcdef,xabddef,xabeef,xabccdef,x12ef,xab44cdef,xabcddef&limit=100&page=2',json={
                "page":2,
                "limit":5,
                "explicit":False,
                "total":1,
                "has_more":False,
                "list":[{"id":"xabcddef"}]
            }, match_querystring=True)
            bat = [
                Episode(1,2,'x123456'),
                Episode(8,3,'xabcdef'),
                Episode(3,3,'xabddef'),
                Episode(4,3,'xabeef'),
                Episode(3,3,'xabccdef'),
                Episode(2,3,'x12ef'),
                Episode(4,3,'xab44cdef'),
                Episode(8,3,'xabcddef')
            ]
            proc_batch(bat)
            self.assertEqual([ep.status for ep in bat], [1,0,1,1,1,1,0,1])
        
    def test_proc_batch_ignores_already_viewed(self):
        with responses.RequestsMock() as rm:
            rm.add(responses.GET,'https://api.dailymotion.com/videos?fields=id&ids=a,b&limit=100&page=1',json={
                "page":1,
                "limit":5,
                "explicit":False,
                "total":1,
                "has_more":False,
                "list":[{"id":"a"}]
            }, match_querystring=True)
            bat = [
                Episode(1,2,'a'),
                Episode(8,3,'b'),
                Episode(3,3,'c', status=0),
                Episode(3,3,'d', status=1)
            ]
            proc_batch(bat)
            self.assertEqual([ep.status for ep in bat], [1,0,0,1])
    
    def test_episode_server_form_response_names_providers(self):
        names = ['Name#1','Name#2']
        response = EpisodeServer.Response(mock.MagicMock(providers=[MockProvider(name) for name in names]), [])
        self.assertEqual(response.providers, names)
        
    def test_episode_server_response_lists_titles(self):
        names = ['Name#1','Name#1']
        resp = EpisodeServer.Response(mock.MagicMock(providers=[MockProvider(name) for name in names]), [
            [
                mock.MagicMock(season=1, episode=1, title='s1ep1', status=1, dailymotion_id='1'),
                mock.MagicMock(season=2, episode=2, title='s2ep2', status=1, dailymotion_id='2')
            ],
            [
                mock.MagicMock(season=1, episode=1, title='s1ep1', status=1, dailymotion_id='3'),
                mock.MagicMock(season=1, episode=2, title='s1ep2', status=1, dailymotion_id='4'),
                mock.MagicMock(season=2, episode=1, title='s2ep1', status=1, dailymotion_id='5'),
            ]
        ])
        self.assertEqual(len(resp.episodes), 4)
        self.assertCountEqual([(ep.season, ep.episode, ep.title) for ep in resp.episodes], [(1,1,'s1ep1'),(1,2,'s1ep2'),(2,1,'s2ep1'),(2,2,'s2ep2')])
        
    def test_episode_server_response_lists_providers(self):
        names = ['Name#1','Name#1']
        resp = EpisodeServer.Response(mock.MagicMock(providers=[MockProvider(name) for name in names]), [
            [
                mock.MagicMock(season=1, episode=1, title='s1ep1', status=1, dailymotion_id='1'),
                mock.MagicMock(season=2, episode=2, title='s2ep2', status=1, dailymotion_id='2')
            ],
            [
                mock.MagicMock(season=1, episode=1, title='s1ep1', status=1, dailymotion_id='3'),
                mock.MagicMock(season=1, episode=2, title='s1ep2', status=1, dailymotion_id='4'),
                mock.MagicMock(season=2, episode=1, title='s2ep1', status=1, dailymotion_id='5'),
            ]
        ])
        self.assertCountEqual([(ep.season, ep.episode, ep.providers) for ep in resp.episodes], [
            (1, 1, {0:'1',1:'3'}),
            (1, 2, {1:'4'}),
            (2, 1, {1:'5'}),
            (2, 2, {0:'2'}),
        ])
        
    def test_episode_server_response_ignores_missing_unchecked(self):
        names = ['Name#1','Name#1']
        resp = EpisodeServer.Response(mock.MagicMock(providers=[MockProvider(name) for name in names]), [
            [
                mock.MagicMock(season=1, episode=1, title='s1ep1', status=-1, dailymotion_id='1'),
                mock.MagicMock(season=1, episode=2, title='s1ep2', status=0, dailymotion_id='2')
            ],
            [
                mock.MagicMock(season=1, episode=1, title='s1ep1', status=1, dailymotion_id='3'),
                mock.MagicMock(season=1, episode=2, title='s1ep2', status=1, dailymotion_id='4'),
                mock.MagicMock(season=1, episode=3, title='s1ep3', status=-1, dailymotion_id='5')
            ]
        ])
        self.assertCountEqual([(ep.season, ep.episode, ep.providers) for ep in resp.episodes], [
            (1, 1, {1:'3'}),
            (1, 2, {1:'4'}),
            (1, 3, {})
        ])
    
    @mock.patch('time.time')
    def test_episode_server_response_as_json(self, time):
        time.return_value = 1337
        names = ['Name#1','Name#1']
        resp = EpisodeServer.Response(mock.MagicMock(providers=[MockProvider(name) for name in names]), [
            [
                mock.MagicMock(season=1, episode=1, title='s1ep1', status=1, dailymotion_id='1'),
                mock.MagicMock(season=1, episode=2, title='s1ep2', status=1, dailymotion_id='2')
            ],
            [
                mock.MagicMock(season=1, episode=1, title='s1ep1', status=1, dailymotion_id='3'),
                mock.MagicMock(season=1, episode=3, title='s1ep3', status=1, dailymotion_id='5')
            ]
        ])
        self.assertCountEqual(resp.as_json(), {
            'time': 1337,
            'providers': names,
            'episodes': [
                {
                    'season': 1,
                    'episode': 1,
                    'title': 's1ep1',
                    'providers': {
                        0: 1,
                        1: 3
                    }
                },
                {
                    'season': 1,
                    'episode': 2,
                    'title': 's1ep2',
                    'providers': {
                        0: 2
                    }
                },
                {
                    'season': 1,
                    'episode': 3,
                    'title': 's1ep3',
                    'providers': {
                        1: 5
                    }
                }
            ]
        })
        
    def test_episode_server_get_data(self):
        episode_layout = [
            [(1,1),(1,2)],
            [(1,2),(1,3)],
            [(1,1),(1,3)]
        ]
        providers = [MockProvider('Provider %d'%i, episode_layout=episode_layout[i], provider_id='abc'[i], episode_status=1) for i in range(3)]
        resp = EpisodeServer(providers).get_data()
        self.assertListEqual([(ep.season, ep.episode, list(ep.providers.keys())) for ep in resp.episodes], [
            (1,1,[0,2]),
            (1,2,[0,1]),
            (1,3,[1,2])
        ])
        
    def test_episode_server_get_data_handles_subproviders(self):
        superprov = MockSuperProvider(['Sub-Prov#1','Sub-Prov#2'],[[(1,1,'a'),(1,2,'b')],[(1,2,'c'),(2,1,'d')]])
        superprov.name = ['Sub-Prov#1','Sub-Prov#2']
        with responses.RequestsMock() as rm:
            rm.add(responses.GET, 'https://api.dailymotion.com/videos?fields=id&ids=a,b,c,d&limit=100&page=1',json={
                "has_more":False,
                "list":[{"id":"a"},{"id":"b"},{"id":"c"},{"id":"d"}]
            }, match_querystring=True)
            resp = EpisodeServer([superprov]).get_data()
        self.assertCountEqual([(ep.season, ep.episode, ep.providers) for ep in resp.episodes], [
            (1,1,{0:'a'}),
            (1,2,{0:'b',1:'c'}),
            (2,1,{1:'d'}),
        ])
        self.assertCountEqual(resp.providers, superprov.name)
    
    def test_episode_server_normally_doesnt_spawn_timer(self):
        with mock.patch('threading.Timer.__init__') as timer_init:
            timer_init.return_value = None
            EpisodeServer(None)
            timer_init.assert_not_called()
    
    def test_episode_server_reset_timer_stops_previous_timer(self):
        es = EpisodeServer(MockProvider('MP', episode_layout=[(1,1)], episode_status=1))
        mock_timer = mock.MagicMock()
        es.timer = mock_timer
        es.reset_timer()
        mock_timer.cancel.assert_called_once()
    
    def test_episode_server_reset_timer_starts_new_timer(self):
        es = EpisodeServer(MockProvider('MP', episode_layout=[(1,1)], episode_status=1))
        es.refresh_rate = 1
        with mock.patch('threading.Timer') as timer:
            es.reset_timer()
            timer.assert_called_once_with(60, mock.ANY, kwargs={'force_refresh':True})
            self.assertTrue(timer.daemon)
            timer.return_value.start.assert_called_once()
    
    def test_episode_server_rejects_delays_less_than_one(self):
        es = EpisodeServer([])
        es.refresh_rate = .5
        self.assertRaises(AssertionError, es.reset_timer)
        es.refresh_rate = 1
        es.reset_timer()
        es.refresh_rate = 0
        es.reset_timer()
    
    def test_episode_server_updates_cache_when_started_with_timer(self):
        es = EpisodeServer([MockProvider('MP', episode_layout=[(1,1)], episode_status=1)], caching_refresh_rate_minutes=1)
        es.pool.close()
        es.pool.join()
        self.assertEqual(es.cache.as_json(), {
            'providers': ['MP'],
            'time': mock.ANY,
            'episodes': [
                {
                    'season': 1,
                    'episode': 1,
                    'title': 's1ep01',
                    'providers': {0:'a-0'}
                }
            ]
        })
    
    def test_episode_server_hash(self):
        es = EpisodeServer(MockProvider('MP', episode_layout=[(1,1),(1,2),(1,3)], episode_status=1))
        self.assertEqual(hash(es), hash(es))
        
class MockProvider:
    # episode_layout format is an array of episodes where each episode is a tuple of season and episodes#
    def __init__(self, name, episode_layout=[], provider_id='a', episode_status=-1):
        self.name = name
        self.episode_layout = episode_layout
        self.provider_id = provider_id
        self.episode_status = episode_status
    
    def get_batch(self):
        return [
            Episode(
                self.episode_layout[i][0],
                self.episode_layout[i][1],
                '%s-%d'%(self.provider_id, i),
                title='s%dep%02d'%self.episode_layout[i],
                status=self.episode_status
            )
            for i
            in range(
                len(
                    self.episode_layout
                )
            )
        ]
    
class MockSuperProvider(MockProvider):
    def get_batch(self):
        return [[Episode(t[0], t[1], t[2], title='s%dep%02d'%(t[0],t[1]), status=self.episode_status) for t in subprov] for subprov in self.episode_layout]
if __name__ == '__main__':
    unittest.main()