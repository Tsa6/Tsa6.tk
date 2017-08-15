import unittest
import time
from mlptkeps.episodeframework import *
        
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
                'x%s-%d'%(self.provider_id, i),
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
        
class DelayingProvider:
    # episode_layout format is an array of episodes where each episode is a tuple of season and episodes#
    def __init__(self, name):
        self.name = name
    
    def get_batch(self):
        time.sleep(60)
    
class MockSuperProvider(MockProvider):
    def get_batch(self):
        return [[Episode(t[0], t[1], t[2], title='s%dep%02d'%(t[0],t[1]), status=self.episode_status) for t in subprov] for subprov in self.episode_layout]
if __name__ == '__main__':
    unittest.main()
