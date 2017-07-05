import requests
import re
from mlptkeps import episodeframework

class DailymotionChannelsProvider(episodeframework.Provider):
    
    def __init__(self, channel_ids, include_regexs, exclude_regexs): #regex lists are 2d and each sub-list matches with the channel id.
        super().__init__(channel_ids)
        self.include_regexs = include_regexs
        self.exclude_regexs = exclude_regexs
    
    def get_batch(self):
        has_more = True
        current_page = 0
        episodes = [[] for i in range(len(self.name))]
        while has_more:
            current_page += 1
            response = requests.get('https://api.dailymotion.com/videos?fields=id,title,owner.username&owners=%s&limit=100&page=%d'%(','.join(self.name),current_page)).json()
            has_more = response['has_more']
            episodes = [
                episodes[i] + [
                    l[0]
                    for l
                    in [
                        [
                            episodeframework.Episode(int(match['s']), int(match['ep']), epres['id'], title=match['title'] if 'title' in match.groupdict() else None, status=1)
                            for match
                            in [
                                re.search(regex, epres['title'], flags=re.I)
                                for regex
                                in self.include_regexs[i]
                            ]
                            if match
                        ]
                        for epres
                        in response['list']
                        if epres['owner.username'] == self.name[i] and len([
                            m
                            for m
                            in [
                                re.search(regex, epres['title'], flags=re.I)
                                for regex
                                in self.exclude_regexs[i]
                            ]
                            if m
                        ]) == 0
                    ]
                    if len(l)
                ]
                for i
                in range(len(self.name))
            ]
            
        return episodes
    
    def parse_from_text(text):
        i = -1
        channel_ids = []
        include_regexs = []
        exclude_regexs = []
        for line in text.splitlines():
            if re.match(r'\s*(#|$)', line):
                pass
            elif re.match(r'\s*@', line):
                i += 1
                channel_ids.append(re.match(r'\s*@\s*(.+?)\s*$', line)[1])
                include_regexs.append([])
                exclude_regexs.append([])
            elif i>= 0 and re.match(r'\s*[\+|-]\s*.+?', line):
                (include_regexs[i] if re.match(r'\s*([\+|-])', line)[1] == '+' else exclude_regexs[i]).append(re.match(r'\s*[\+|-]\s*(.+?)\s*$', line)[1])
        return DailymotionChannelsProvider(channel_ids, include_regexs, exclude_regexs)
    
    def parse_from_url(url):
        return DailymotionChannelsProvider.parse_from_text(requests.get(url).text)
    
    def parse_from_file(filename):
        with open(filename, 'r') as file:
            return DailymotionChannelsProvider.parse_from_text(file.read(-1))