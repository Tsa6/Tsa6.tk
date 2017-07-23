from abc import *
import requests
import time
import threading
import multiprocessing
import operator

class Episode():
    
    def __init__(self, season, episode, dailymotion_id, status=-1, title=None):
        if any([char in str(dailymotion_id) for char in '<>&"/\'']):
            raise ValueError('Illegal character in dailymotion_id [%s]'%dailymotion_id)
        self.season = season
        self.episode = episode
        self.dailymotion_id = dailymotion_id
        self.status = status
        self.title = title
    
    def __eq__(self, other):
        return (self.season, self.episode, self.dailymotion_id, self.title) == (other.season, other.episode, other.dailymotion_id, other.title)
    
    def __str__(self):
        return 's%dep%d - \'%s\''%(self.season, self.episode, self.title)
    
    def __repr__(self):
        return '%s (%s)'%(self, self.dailymotion_id)
    
    def __lt__(self, other):
        return int(self) < int(other)
    
    def __gt__(self, other):
        return int(self) > int(other)
    
    def __le__(self, other):
        return int(self) <= int(other)
    
    def __ge__(self, other):
        return int(self) >= int(other)
    
    def __ne__(self, other):
        return not(self == other)
    
    def __int__(self):
        return self.season * 100 + self.episode
    
class Provider(ABC):
    
    def __init__(self,name): #Name can be either one string, a a list of strings which are the names for sub-providers
        self.name = name
    
    # Returns either a list of episodes, or list of lists of episodes, one for each sub-provider
    @abstractmethod#pragma: no cover
    def get_batch(self):
        pass

class EpisodeServer:
    
    class Response():
        class MultiSourceEpisode(Episode):
            def __init__(self, obj):
                super().__init__(obj['s'], obj['ep'], None, title=obj['title'], status=-2)
                self.providers = obj['provs']
            
        def __init__(self, episode_server, episodes2D):
            self.providers = [prov.name for prov in episode_server.providers]
            i = 0
            while i < len(self.providers):
                if type(self.providers[i]) is list:
                    [self.providers.insert(i, name) for name in reversed(self.providers.pop(i))]
                    i -= 1
                i += 1
            self.time = int(time.time())
            episodes = {}
            for i in range(len(episodes2D)):
                prov = episodes2D[i]
                for ep in prov:
                    epstr = 's%dep%d'%(ep.season, ep.episode)
                    if epstr not in episodes:
                        episodes[epstr] = {
                            's':ep.season,
                            'ep':ep.episode,
                            'title':ep.title,
                            'provs':{}
                        }
                    if ep.status == 1:
                        episodes[epstr]['provs'][i] = ep.dailymotion_id
                    if episodes[epstr]['title'] == None and ep.title:
                        episodes[epstr]['title'] = ep.title
            self.episodes = [EpisodeServer.Response.MultiSourceEpisode(o) for o in episodes.values()]
            self.hash = hash(self)
        
        def __eq__(self, other):
            return type(self) == type(other) and hash(self) == hash(other)
        
        def __hash__(self):
            return hash(tuple([
                tuple(self.providers)
            ] + [
                (ep.season, ep.episode, ep.title, ep.status, tuple(ep.providers.keys()), tuple(ep.providers.values()))
                for ep
                in self.episodes
            ]))
        
        def as_json(self):
            return {'providers': self.providers, 'time':self.time, 'episodes':[{'season': ep.season, 'episode':ep.episode, 'title': ep.title, 'providers': ep.providers} for ep in self.episodes]}
    
    def __init__(self, providers, caching_refresh_rate_minutes=0, pool_size=3):
        self.providers = providers
        self.refresh_rate = caching_refresh_rate_minutes
        self.cache = None
        self.timer = None
        self.pool = multiprocessing.Pool(pool_size)
        self.lock = threading.Lock()
        if caching_refresh_rate_minutes:
            self.update_cache_async()
        
    def reset_timer(self):
        assert self.refresh_rate == 0 or self.refresh_rate >= 1
        if self.timer:
            self.timer.cancel()
        if self.refresh_rate:
            self.timer = threading.Timer(60 * self.refresh_rate, self.get_data, kwargs={'force_refresh':True})
            self.timer.daemon = True
            self.timer.start()
    
    def get_data(self, force_refresh = False):
        with self.lock:
            if force_refresh or not (self.refresh_rate and self.cache):
                self.reset_timer()
                episodes2D = self.pool.imap(operator.methodcaller('get_batch'), self.providers)
                self.cache = EpisodeServer.Response(self, EpisodeServer._raw_prov_result_to_ready_for_result(episodes2D))
            return self.cache
        
    def _raw_prov_result_to_ready_for_result(episodes2D):
        episodes = []
        for lmnt in episodes2D:
            if len(lmnt) > 0 and type(lmnt[0]) is list:
                episodes += lmnt
            else:
                episodes.append(lmnt)
        proc_batch([ep for row in episodes for ep in row])
        return episodes
    
    def _sync_process_provs_static(provs):
        episodes2D = map(operator.methodcaller('get_batch'), provs)
        return EpisodeServer._raw_prov_result_to_ready_for_result(episodes2D)
    
    def update_cache_async(self):
        class CacheSetter:
            def __init__(self, eps):
                self.eps = eps
            def __call__(self, value):
                self.eps.cache = EpisodeServer.Response(self.eps, value)
                self.eps.lock.release()
        def raiseit(ex):
            raise ex
        self.lock.acquire()
        self.pool.apply_async(EpisodeServer._sync_process_provs_static, [self.providers], callback=CacheSetter(self), error_callback=raiseit)
        self.reset_timer()
            
        
    
def proc_batch(episodes):
    episodes_filtered = [ep for ep in episodes if ep.status == -1]
    current_page = 0
    more_pages = True
    valid_ids = []
    while more_pages:
        current_page += 1
        resp = requests.get('https://api.dailymotion.com/videos?fields=id&ids=%s&limit=100&page=%d'%(','.join(map(lambda ep: ep.dailymotion_id, episodes_filtered)), current_page)).json()
        more_pages = resp['has_more']
        valid_ids += map(lambda res: res['id'], resp['list'])
    for episode in episodes_filtered:
        episode.status = valid_ids.count(episode.dailymotion_id) # Should by either 0 or 1, 0 if episode was not found in search, 1 if it was.  Dailymotion shouldn't list duplicates
