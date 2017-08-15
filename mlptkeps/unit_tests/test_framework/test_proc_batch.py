import responses
import unittest
from mlptkeps.episodeframework import *
from . import *

class TestProcBatch(unittest.TestCase):
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
            rm.add(responses.GET,'https://api.dailymotion.com/videos?fields=id&ids=xa,xb&limit=100&page=1',json={
                "page":1,
                "limit":5,
                "explicit":False,
                "total":1,
                "has_more":False,
                "list":[{"id":"xa"}]
            }, match_querystring=True)
            bat = [
                Episode(1,2,'xa'),
                Episode(8,3,'xb'),
                Episode(3,3,'xc', status=0),
                Episode(3,3,'xd', status=1)
            ]
            proc_batch(bat)
            self.assertEqual([ep.status for ep in bat], [1,0,0,1])
    
    def test_proc_batch_checks_nonxids(self):
        with responses.RequestsMock() as rm:
            rm.add(responses.GET,'https://api.dailymotion.com/video/scootaloo', json = {
                'not-an-error': True
            })
            rm.add(responses.GET,'https://api.dailymotion.com/video/badseed', json = {
                'error': 'what we gonna do?'
            })
            bat = [
                    Episode(1,1,'scootaloo'),
                    Episode(1,2,'badseed'),
            ]
            proc_batch(bat)
            self.assertEqual([ep.status for ep in bat], [1,0])

    def test_proc_batch_ignore_notavailable(self):
        with responses.RequestsMock() as rm: #No outward bound connections, ya here?!
            bat = [
                Episode(1,3,'NotAvailable')
            ]
            proc_batch(bat)
            self.assertEqual(bat[0].status, 0)
