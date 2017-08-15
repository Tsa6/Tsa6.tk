import responses
import unittest
import time
import threading
from unittest import mock
from mlptkeps.episodeframework import *
from . import *

class TestEpisodeServer(unittest.TestCase):
    
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
        
    def test_episode_server_response_fills_in_missing_titles(self):
        names = ['Name#1','Name#1']
        resp = EpisodeServer.Response(mock.MagicMock(providers=[MockProvider(name) for name in names]), [
            [
                Episode(1, 1, '1', status=1),
            ],
            [
                Episode(1, 1, '2', title='Correct title', status=1),
            ],
        ])
        self.assertCountEqual([ep.title for ep in resp.episodes], ['Correct title'])
        
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
        
    def test_episode_server_get_data_uses_cache(self):
        episode_layout = [
            [(1,1),(1,2)],
            [(1,2),(1,3)],
            [(1,1),(1,3)]
        ]
        providers = [MockProvider('Provider %d'%i, episode_layout=episode_layout[i], provider_id='abc'[i], episode_status=1) for i in range(3)]
        es = EpisodeServer(providers)
        es.refresh_rate = 10;
        a = es.get_data()
        for p in providers:
            p.episode_layout = None
        
        self.assertEqual(a, es.get_data())
        
    def test_episode_server_get_data_requires_lock(self):
        es = EpisodeServer([MockProvider('DP')])
        es.lock.acquire()
        t = threading.Thread(target=es.get_data)
        t.start()
        t.join(timeout=.5)
        self.assertTrue(t.is_alive())
        es.lock.release()
        t.join()
        self.assertFalse(t.is_alive())
        
    def test_episode_server_update_cache(self):
        es = EpisodeServer([
            MockProvider('MP1', episode_layout=[(1,1),(1,2)], provider_id='a'),
            MockProvider('MP2', episode_layout=[(1,2),(1,3)], provider_id='b')
        ])
        es.update_cache_async()
        self.assertCountEqual(es.cache.as_json(), {
            'time': mock.ANY,
            'providers': ['MP1','MP2'],
            'episodes': [
                {
                    'season': 1,
                    'episode': 1,
                    'title': 's1ep01',
                    'providers': {
                        0: 'a-0',
                    }
                },
                {
                    'season': 1,
                    'episode': 2,
                    'title': 's1ep02',
                    'providers': {
                        0: 'a-1',
                        1: 'b-0'
                    }
                },
                {
                    'season': 1,
                    'episode': 3,
                    'title': 's1ep03',
                    'providers': {
                        1: 'b-1'
                    }
                }
            ]
        })
        
    def test_episode_server_get_data_handles_subproviders(self):
        superprov = MockSuperProvider(['Sub-Prov#1','Sub-Prov#2'],[[(1,1,'xa'),(1,2,'xb')],[(1,2,'xc'),(2,1,'xd')]])
        superprov.name = ['Sub-Prov#1','Sub-Prov#2']
        with responses.RequestsMock() as rm:
            rm.add(responses.GET, 'https://api.dailymotion.com/videos?fields=id&ids=xa,xb,xc,xd&limit=100&page=1',json={
                "has_more":False,
                "list":[{"id":"xa"},{"id":"xb"},{"id":"xc"},{"id":"xd"}]
            }, match_querystring=True)
            resp = EpisodeServer([superprov]).get_data()
        self.assertCountEqual([(ep.season, ep.episode, ep.providers) for ep in resp.episodes], [
            (1,1,{0:'xa'}),
            (1,2,{0:'xb',1:'xc'}),
            (2,1,{1:'xd'}),
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
        self.assertEqual(es.cache.as_json(), {
            'providers': ['MP'],
            'time': mock.ANY,
            'episodes': [
                {
                    'season': 1,
                    'episode': 1,
                    'title': 's1ep01',
                    'providers': {0:'xa-0'}
                }
            ]
        })
    
    def test_episode_server_response_hash(self):
        es = EpisodeServer([MockProvider('MP', episode_layout=[(1,1),(1,2),(1,3)], episode_status=1)])
        r1 = es.get_data()
        r2 = es.get_data()
        self.assertEqual(hash(r1), hash(r2))
    
    def test_episode_server_response_equality(self):
        es = EpisodeServer([MockProvider('MP', episode_layout=[(1,1),(1,2),(1,3)], episode_status=1)])
        r1 = es.get_data()
        r2 = es.get_data()
        self.assertEqual(r1, r2)
