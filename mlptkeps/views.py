from django.http import HttpResponse
from django.utils import cache
from django import views
from bs4 import BeautifulSoup
import re
import json
from mlptkeps import util

#Should be defined with episode_server property filled with an episodeframework.EpisodeServer
class TableView(views.View):

    def __init__(self, episode_server):
        self.episode_server = episode_server
    
    def get_soup(self):
        data = self.episode_server.get_data()
        data.episodes.sort()
        soup = None
        with open('mlptkeps/TableResponse.html','r') as base_page:
            soup = BeautifulSoup(base_page,'lxml')
        for provider in data.providers:
            th = soup.new_tag('th')
            th.string = util.html_sanitize(provider)
            soup.thead.tr.append(th)
        for ep in data.episodes:
            row = soup.new_tag('tr')
            row['class'] = 'episode'
            
            ep_data = soup.new_tag('td',sorttable_customkey='%d%02d'%(ep.season, ep.episode))
            ep_data.string = 'Season %d Episode %d'%(ep.season, ep.episode)
            row.append(ep_data)
            
            ep_title = soup.new_tag('td')
            ep_title.string = util.html_sanitize(ep.title)
            ep_title['class'] = 'title'
            row.append(ep_title)
            
            percent = len(ep.providers)/len(data.providers)
            ep_sources = soup.new_tag('td', style='background-color:hsl(%d,100%%,%d%%)'%(16 + 68 * percent, 66 - 7 * percent))
            ep_sources.string = str(len(ep.providers))
            row.append(ep_sources)
            
            for i in range(len(data.providers)):
                avail = [int(k) for k in ep.providers.keys()].count(i)
                ep_avail = soup.new_tag('td',sorttable_customkey=avail)
                if avail:
                    lnk = soup.new_tag('a', href='https://www.dailymotion.com/video/%s'%(ep.providers[i]))
                    lnk.string = 'Yes'
                    ep_avail.append(lnk)
                else:
                    ep_avail.string = 'No'
                row.append(ep_avail)
            
            soup.tbody.append(row)
        return soup
    
    def get(self, req):
        if self.episode_server.refresh_rate and self.episode_server.cache and 'HTTP_IF_NONE_MATCH' in req.META and req.META['HTTP_IF_NONE_MATCH'] == gen_etag(self.episode_server.cache.hash):
            return HttpResponse(status=304)
        return addCacheHeaders(HttpResponse(self.get_soup().prettify()), self.episode_server.cache.hash)

class JsonView(views.View):

    def __init__(self, episode_server):
        self.episode_server = episode_server
        
    def get(self, req):
        if self.episode_server.refresh_rate and self.episode_server.cache and 'HTTP_IF_NONE_MATCH' in req.META and req.META['HTTP_IF_NONE_MATCH'] == gen_etag(self.episode_server.cache.hash):
            return HttpResponse(status=304)
        resp = addCacheHeaders(HttpResponse(json.dumps(self.episode_server.get_data().as_json(), indent=4), content_type='text/json'), self.episode_server.cache.hash)
        resp['Access-Control-Allow-Origin'] = '*'
        return resp

class EpisodesJsView(views.View):

    def __init__(self, episode_server):
        self.episode_server = episode_server
    
    def get_json(self):
        output = []
        for episode in sorted(self.episode_server.get_data().episodes):
            while len(output) < episode.season:
                output.append([])
            while len(output[episode.season - 1]) < episode.episode - 1:
                output[episode.season - 1].append({
                    'title': 'Unknown Title',
                    'dailymotion': '//www.dailymotion.com/video/NotAvailable',
                    'available': False
                })
            output[episode.season - 1].append({
                'title':util.sanitize_html(episode.title),
                'dailymotion':'//www.dailymotion.com/video/%s'%(
                    list(episode.providers.values())[0]
                    if len(episode.providers)
                    else 'NotAvailable'
                ),
                'available':len(episode.providers) > 0
            })
        return output
        
    def get(self, req):
        if self.episode_server.refresh_rate and self.episode_server.cache and 'HTTP_IF_NONE_MATCH' in req.META and req.META['HTTP_IF_NONE_MATCH'] == gen_etag(self.episode_server.cache.hash):
            return HttpResponse(status=304)
        resp = HttpResponse(re.sub(r'/\*\s*Dynamic Content\s*\*/', json.dumps(self.get_json(), indent=4), open('mlptkeps/EpisodesJsResponse.js').read(-1)), content_type='text/javascript')
        resp['Access-Control-Allow-Origin'] = '*'
        return addCacheHeaders(resp, self.episode_server.cache.hash)

class MissingView(views.View):
    
    def get(self, req):
        qs = req.META['QUERY_STRING'].split('x')
        if len(qs) < 2:
            return HttpResponse(open('mlptkeps/MissingResponse.html').read(-1))
        else:
            return HttpResponse(open('mlptkeps/MissingResponse.html').read(-1).replace('data:text/html;base64,RXJyb3IhICBQbGVhc2UgY29udGFjdCB0c2E2Z2FtZXNAZ21haWwuY29tIHNvIGhlIGNhbiBmaXggdGhpcy4=','https://yp.coco-pommel.org/ypvideo/YP-1R-%sx%s.mkv'%(('00%s'%qs[0])[-2:],('00%s'%qs[1])[-2:])))

def addCacheHeaders(resp, hash_int):
    cache.patch_response_headers(resp, cache_timeout=600)
    cache.patch_cache_control(resp, stale_if_error=60 * 60 *24, stale_while_revalidate=60*60)
    resp['Content-Language'] = 'en'
    resp['ETag'] = gen_etag(hash_int)
    return resp

def gen_etag(hash_int):
    return hex(hash_int)[2:]