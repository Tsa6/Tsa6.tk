from mlptkeps import episodeframework
import requests
import json
import re
import sys

class Evert(episodeframework.Provider):
    
    def __init__(self):
        super().__init__("MLP-Episodes.tk")
        
    def get_batch(self):
        resp = requests.get('https://mlp-episodes.tk/js/episodes.js', headers = {'user-agent':'MLPTK-Browser/2.0 (Contact tsa6games@gmail.com) Python/%d.%d.%d'%(sys.version_info.major,sys.version_info.minor,sys.version_info.micro)})
        json_text = None
        end = False
        parsed = None
        for line in resp.iter_lines(): # Pragma: No branch
            line = line.decode('utf-8')
            if line.startswith('var episodes = '):
                line = line.replace('var episodes = ','')
                json_text = ''
            if json_text != None:
                if(line.endswith(';')):
                    end = True
                    line = line.replace(';','')
                json_text += line.strip()
                if end:
                    parsed = json.loads(json_text)
                    break
        if not(parsed):
            raise Exception('Unexpected EOF (%s)'%(json_text == None))
        return_arr = [];
        for s in range(len(parsed)):
            for ep in range(len(parsed[s])):
                return_arr.append(episodeframework.Episode(s + 1, ep + 1, re.search(r'video\/([^-_]+)', parsed[s][ep]['dailymotion']).group(1), title=parsed[s][ep]['title']))
        return return_arr;