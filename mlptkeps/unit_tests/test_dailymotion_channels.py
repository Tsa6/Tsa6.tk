import responses
import unittest
from unittest import mock
from mlptkeps.providers.dailymotion_channels import *
from mlptkeps import episodeframework

class TestDailymotionChannels(unittest.TestCase):
    
    def test_get_batch_captures_valid_episodes(self):
        dcp = DailymotionChannelsProvider(['channel-name'],[[r's(?P<s>\d)ep(?P<ep>\d{1,2}) (?P<title>.+)']],[[]])
        with responses.RequestsMock() as rm:
            rm.add(responses.GET,'https://api.dailymotion.com/videos?fields=id,title,owner.username&owners=channel-name&limit=100&page=1',json={
                "has_more":False,
                "list":[
                    {"id":"id01","title":"s1ep1 Pilot","owner.username":"channel-name"},
                    {"id":"id02","title":"s1ep2 Another Episode","owner.username":"channel-name"},
                    {"id":"id03","title":"Wrong Video","owner.username":"channel-name"}
                ]
            },match_querystring=True)
            self.assertCountEqual(dcp.get_batch(),[
                [
                    episodeframework.Episode(1, 1, 'id01', title='Pilot'),
                    episodeframework.Episode(1, 2, 'id02', title='Another Episode')
                ]
            ])
    
    def test_get_batch_captures_ignores_bad_episodes(self):
        dcp = DailymotionChannelsProvider(['channel-name'],[[r's(?P<s>\d)ep(?P<ep>\d{1,2}) (?P<title>.+)']],[['\[Spanish\]']])
        with responses.RequestsMock() as rm:
            rm.add(responses.GET,'https://api.dailymotion.com/videos?fields=id,title,owner.username&owners=channel-name&limit=100&page=1',json={
                "has_more":False,
                "list":[
                    {"id":"id01","title":"s1ep1 Pilot","owner.username":"channel-name"},
                    {"id":"id02","title":"s1ep2 Another Episode [Spanish]","owner.username":"channel-name"},
                ]
            },match_querystring=True)
            self.assertCountEqual(dcp.get_batch(),[[episodeframework.Episode(1, 1, 'id01', title='Pilot')]])
    
    def test_get_batch_captures_can_seperate_channels(self):
        dcp = DailymotionChannelsProvider(['channel1','channel2'],[[r's(?P<s>\d)ep(?P<ep>\d{1,2}) (?P<title>.+)'],[r's(?P<s>\d)ep(?P<ep>\d{1,2}) (?P<title>.+)']],[[],[]])
        with responses.RequestsMock() as rm:
            rm.add(responses.GET,'https://api.dailymotion.com/videos?fields=id,title,owner.username&owners=channel1,channel2&limit=100&page=1',json={
                "has_more":False,
                "list":[
                    {"id":"id01","title":"s1ep1 Pilot","owner.username":"channel1"},
                    {"id":"id02","title":"s1ep2 Another Episode","owner.username":"channel1"},
                    {"id":"id03","title":"s1ep2 Another Episode","owner.username":"channel2"},
                    {"id":"id04","title":"s1ep3 They Just Keep Comming","owner.username":"channel2"},
                ]
            },match_querystring=True)
            self.assertCountEqual(dcp.get_batch(),[
                [
                    episodeframework.Episode(1, 1, 'id01', title='Pilot'),
                    episodeframework.Episode(1, 2, 'id02', title='Another Episode')
                ],
                [
                    episodeframework.Episode(1, 2, 'id03', title='Another Episode'),
                    episodeframework.Episode(1, 3, 'id04', title='They Just Keep Comming')
                ]
            ])
    
    def test_get_batch_captures_can_seperate_regexs(self):
        dcp = DailymotionChannelsProvider(['channel1','channel2'],[[r'\[a\] s(?P<s>\d)ep(?P<ep>\d{1,2}) (?P<title>.+)'],[r'\[b\] s(?P<s>\d)ep(?P<ep>\d{1,2}) (?P<title>.+)']],[[r'\[a-ign\]'],[r'\[b-ign\]']])
        with responses.RequestsMock() as rm:
            rm.add(responses.GET,'https://api.dailymotion.com/videos?fields=id,title,owner.username&owners=channel1,channel2&limit=100&page=1',json={
                "has_more":False,
                "list":[
                    {"id":"id01","title":"[a] s1ep1 Pilot","owner.username":"channel1"},
                    {"id":"id02","title":"[a] s1ep2 Another Episode [a-ign]","owner.username":"channel1"},
                    {"id":"id03","title":"[b] s1ep2 Another Episode","owner.username":"channel2"},
                    {"id":"id04","title":"[b] s1ep3 They Just Keep Comming [b-ign]","owner.username":"channel2"},
                ]
            },match_querystring=True)
            self.assertCountEqual(dcp.get_batch(),[
                [
                    episodeframework.Episode(1, 1, 'id01', title='Pilot'),
                ],
                [
                    episodeframework.Episode(1, 2, 'id03', title='Another Episode'),
                ]
            ])
    
    def test_get_batch_works_with_multiline_responses(self):
        dcp = DailymotionChannelsProvider(['channel1'],[[r's(?P<s>\d)ep(?P<ep>\d{1,2}) (?P<title>.+)']],[[r'ignore']])
        with responses.RequestsMock() as rm:
            rm.add(responses.GET,'https://api.dailymotion.com/videos?fields=id,title,owner.username&owners=channel1&limit=100&page=1',json={
                "has_more":True,
                "list":[
                    {"id":"id01","title":"s1ep1 Pilot","owner.username":"channel1"},
                    {"id":"id02","title":"s1ep2 Another Episode ignore","owner.username":"channel1"}
                ]
            },match_querystring=True)
            rm.add(responses.GET,'https://api.dailymotion.com/videos?fields=id,title,owner.username&owners=channel1&limit=100&page=2',json={
                "has_more":False,
                "list":[
                    {"id":"id03","title":"s1ep2 Another Episode","owner.username":"channel1"},
                    {"id":"id04","title":"s1ep3 They Just Keep Comming ignore","owner.username":"channel1"},
                ]
            },match_querystring=True)
            self.assertCountEqual(dcp.get_batch(),[
                [
                    episodeframework.Episode(1, 1, 'id01', title='Pilot'),
                    episodeframework.Episode(1, 2, 'id03', title='Another Episode'),
                ]
            ])
    
    def test_get_batch_works_with_no_title_match_group(self):
        dcp = DailymotionChannelsProvider(['channel1'],[[r's(?P<s>\d)ep(?P<ep>\d{1,2})']],[[]])
        with responses.RequestsMock() as rm:
            rm.add(responses.GET,'https://api.dailymotion.com/videos?fields=id,title,owner.username&owners=channel1&limit=100&page=1',json={
                "has_more":False,
                "list":[
                    {"id":"id01","title":"s1ep1","owner.username":"channel1"},
                    {"id":"id02","title":"s1ep2","owner.username":"channel1"}
                ]
            },match_querystring=True)
            self.assertCountEqual(dcp.get_batch(),[
                [
                    episodeframework.Episode(1, 1, 'id01'),
                    episodeframework.Episode(1, 2, 'id02'),
                ]
            ])
    
    def test_get_batch_case_insensetive(self):
        dcp = DailymotionChannelsProvider(['channel1'],[[r's(?P<s>\d)ep(?P<ep>\d{1,2})\s*(?P<title>.+)']],[[]])
        with responses.RequestsMock() as rm:
            rm.add(responses.GET,'https://api.dailymotion.com/videos?fields=id,title,owner.username&owners=channel1&limit=100&page=1',json={
                "has_more":False,
                "list":[
                    {"id":"id01","title":"S1ep1 title1","owner.username":"channel1"},
                    {"id":"id02","title":"s1EP2 title2","owner.username":"channel1"}
                ]
            },match_querystring=True)
            self.assertCountEqual(dcp.get_batch(),[
                [
                    episodeframework.Episode(1, 1, 'id01', title='title1'),
                    episodeframework.Episode(1, 2, 'id02', title='title2'),
                ]
            ])
        
    def test_parse_from_text(self):
        dcp = DailymotionChannelsProvider.parse_from_text("""
        @channelname
        + Include Regex
        - Exclude Regex
        """)
        self.assertEqual(dcp.name,['channelname'])
        self.assertEqual(dcp.include_regexs,[['Include Regex']])
        self.assertEqual(dcp.exclude_regexs,[['Exclude Regex']])
        
    def test_parse_from_text_multiple_channels(self):
        dcp = DailymotionChannelsProvider.parse_from_text("""
        @channelname
        + Include Regex
        - Exclude Regex
        
        @channelname2
        + Include Regex 2
        - Exclude Regex 2
        """)
        self.assertEqual(dcp.name,['channelname','channelname2'])
        self.assertEqual(dcp.include_regexs,[['Include Regex'],['Include Regex 2']])
        self.assertEqual(dcp.exclude_regexs,[['Exclude Regex'], ['Exclude Regex 2']])
        
    def test_parse_from_text_comments(self):
        dcp = DailymotionChannelsProvider.parse_from_text("""
        # Ignore This
        @channelname
                                
        + Include Regex
        # This Too
        - Exclude Regex
        """)
        self.assertEqual(dcp.name,['channelname'])
        self.assertEqual(dcp.include_regexs,[['Include Regex']])
        self.assertEqual(dcp.exclude_regexs,[['Exclude Regex']])
        
    @mock.patch('mlptkeps.providers.dailymotion_channels.DailymotionChannelsProvider.parse_from_text')
    def test_parse_from_url(self, parse_from_text):
        with responses.RequestsMock() as rm:
            rm.add(responses.GET, 'http://example.com', body = "Provided body")
            dcp = DailymotionChannelsProvider.parse_from_url('http://example.com')
        parse_from_text.assert_called_with('Provided body')