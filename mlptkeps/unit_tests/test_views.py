from bs4 import BeautifulSoup
import responses
import unittest
from unittest import mock
from mlptkeps import episodeframework
from mlptkeps.views import *
from mlptkeps.unit_tests import test_framework

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
        "list":[{"id":"a-1"},{"id":"a-2"},{"id":"b-0"},{"id":"b-1"},{"id":"b-2"}]
    }
    
    def setUp(self):
        self.epserve = episodeframework.EpisodeServer(
            [
                test_framework.MockProvider(
                    'ProvMock',
                    TestViews.episode_layout[i],
                    provider_id='abcdefg'[i]
                )
                for i
                in range(
                    len(
                        TestViews.episode_layout
                    )
                )
            ]
        )
    
#    def test_table_view_soup(self):
#        table_view = TableView(self.epserve)
#        with responses.RequestsMock() as rm:
#            rm.add(responses.GET, 'https://api.dailymotion.com/videos?fields=id&ids=epid0x0,epid0x1,epid0x2,epid0x3,epid1x0,epid1x1,epid1x2&limit=100&page=1',json=TestViews.js_response,match_querystring=True)
#            with open('mlptkeps/unit_tests/table_response_result.html','r') as target_result:
#                self.assertEqual(table_view.get_soup().prettify(),BeautifulSoup(target_result,'lxml').prettify())
    
    def test_table_view_sanitary(self):
        mock_es = mock.MagicMock(
            providers=[
                mock.MagicMock()
            ],
            cache= mock.MagicMock(hash=1337)
        )
        mock_es.providers[0].name = '<script>'
        mock_es.get_data.return_value = episodeframework.EpisodeServer.Response(mock_es, [[
            episodeframework.Episode(1,1,'id1',status=1,title='<script>')
        ]])
        epjs_view = EpisodesJsView(mock_es)
        for element in mock_es.get_soup().find_all(True):
            self.assertNotRegex(element.string, r'[<>]')
    
    def test_epjs_view_json(self):
        epjs_view = EpisodesJsView(self.epserve)
        with responses.RequestsMock() as rm:
            rm.add(responses.GET, 'https://api.dailymotion.com/videos?fields=id&ids=a-0,a-1,a-2,a-3,b-0,b-1,b-2&limit=100&page=1',json=TestViews.js_response,match_querystring=True)
            self.assertEqual(epjs_view.get_json(),[
                [
                    {
                      "title": "s1ep01",
                      "dailymotion": "//www.dailymotion.com/video/b-0",
                      "available": True
                    },
                    {
                      "title": "s1ep02",
                      "dailymotion": "//www.dailymotion.com/video/b-1",
                      "available": True
                    },
                ],
                [
                    {
                      "title": "s2ep01",
                      "dailymotion": "//www.dailymotion.com/video/a-1",
                      "available": True
                    },
                    {
                      "title": "s2ep02",
                      "dailymotion": "//www.dailymotion.com/video/a-2",
                      "available": True
                    },
                ],
                [
                    {
                      "title": "s3ep01",
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
        