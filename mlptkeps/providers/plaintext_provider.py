import requests
import re
from mlptkeps import episodeframework

def parse_text(text):
    return [
        episodeframework.Episode(int(match[1]), int(match[2]), match[3], title=match[4])
        for match
        in [
            re.match(r'^\s*(\d+) (\d+) (x[a-z\d]+) (.+?)\s*$', line)
            for line
            in text.splitlines()
            if not re.match(r'\s*(#|$)', line)
        ] if match
    ]

class PlaintextProvider(episodeframework.Provider):
    
    def __init__(self, get_text_function, name='Plaintext', parse_function=parse_text):
        self.get_text_function = get_text_function
        self.name=name
        self.parse_function = parse_function
        
    def get_batch(self):
        return self.parse_function(self.get_text_function())
    
    def for_url(url, name='Plaintext', parse_function=parse_text):
        return PlaintextProvider(URLReader(url), name=name, parse_function=parse_function)
    
    def for_file(filename, name='Plaintext', parse_function=parse_text):
        return PlaintextProvider(FileReader(filename), name=name, parse_function=parse_function)

class URLReader():
    def __init__(self,url):
        self.url = url
    def __call__(self):
        return requests.get(self.url).text

class FilerReader():
    def __init__(self,name):
        self.name = name
    def __call__(self):
        with open(self.name) as file:
            return file.read(-1)