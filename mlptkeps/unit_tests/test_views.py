from bs4 import BeautifulSoup
import responses
import unittest
from unittest import mock
from mlptkeps import episodeframework
from mlptkeps.views import *

class TestViews(unittest.TestCase):
    episode_layout = [
        [
            (1,1),
            (2,1),
            (2,2),
            (3,1)
        ],
        [
            (1,1),
            (1,2),
            (2,2)
        ]
    ]
    js_response = {
        "page":1,
        "limit":100,
        "explicit":False,
        "total":1,
        "has_more":False,
        "list":[{"id":"epid0x1"},{"id":"epid0x2"},{"id":"epid1x0"},{"id":"epid1x1"},{"id":"epid1x2"}]
    }
    
    def setUp(self):
        self.epserve = episodeframework.EpisodeServer([prov.configure_mock(name='ProvMock') or prov for prov in [
            mock.MagicMock(get_batch=mock.MagicMock(return_value=[
                episodeframework.Episode(TestViews.episode_layout[i][j][0],TestViews.episode_layout[i][j][1],'epid%dx%d'%(i,j), title='s%dep%d'%TestViews.episode_layout[i][j])
                for j in range(0, len(TestViews.episode_layout[i]))
            ])) for i in range(0,2)
        ]])
    
#    def test_table_view_soup(self):
#        table_view = TableView(self.epserve)
#        with responses.RequestsMock() as rm:
#            rm.add(responses.GET, 'https://api.dailymotion.com/videos?fields=id&ids=epid0x0,epid0x1,epid0x2,epid0x3,epid1x0,epid1x1,epid1x2&limit=100&page=1',json=TestViews.js_response,match_querystring=True)
#            with open('mlptkeps/unit_tests/table_response_result.html','r') as target_result:
#                self.assertEqual(table_view.get_soup().prettify(),BeautifulSoup(target_result,'lxml').prettify())
    
    def test_epjs_view_json(self):
        epjs_view = EpisodesJsView(self.epserve)
        with responses.RequestsMock() as rm:
            rm.add(responses.GET, 'https://api.dailymotion.com/videos?fields=id&ids=epid0x0,epid0x1,epid0x2,epid0x3,epid1x0,epid1x1,epid1x2&limit=100&page=1',json=TestViews.js_response,match_querystring=True)
            self.assertEqual(epjs_view.get_json(),[
                [
                    {
                      "title": "s1ep1",
                      "dailymotion": "//www.dailymotion.com/video/epid1x0",
                      "available": True
                    },
                    {
                      "title": "s1ep2",
                      "dailymotion": "//www.dailymotion.com/video/epid1x1",
                      "available": True
                    },
                ],
                [
                    {
                      "title": "s2ep1",
                      "dailymotion": "//www.dailymotion.com/video/epid0x1",
                      "available": True
                    },
                    {
                      "title": "s2ep2",
                      "dailymotion": "//www.dailymotion.com/video/epid0x2",
                      "available": True
                    },
                ],
                [
                    {
                      "title": "s3ep1",
                      "dailymotion": "//www.dailymotion.com/video/NotAvailable",
                      "available": False
                    },
                ],
            ])
    
    def test_epjs_view_json_fills_gaps(self):
        mock_es = mock.MagicMock(
            providers=[
                mock.MagicMock()
            ],
            cache= mock.MagicMock(hash=1337)
        )
        mock_es.providers[0].name = 'Mock-Provider'
        mock_es.get_data.return_value = episodeframework.EpisodeServer.Response(mock_es, [[
            episodeframework.Episode(1,1,'id1',status=1,title='Scootaloo'),
            episodeframework.Episode(1,3,'id2',status=1,title='BestPony')
        ]])
        epjs_view = EpisodesJsView(mock_es)
        self.assertEqual(epjs_view.get_json(), [
            [
                    {
                      "title": "Scootaloo",
                      "dailymotion": "//www.dailymotion.com/video/id1",
                      "available": True
                    },
                    {
                      "title": mock.ANY,
                      "dailymotion": mock.ANY,
                      "available": False
                    },
                    {
                      "title": "BestPony",
                      "dailymotion": "//www.dailymotion.com/video/id2",
                      "available": True
                    },
            ]
        ])
        