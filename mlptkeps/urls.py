from django.conf.urls import url
from . import views
from mlptkeps.episodeframework import EpisodeServer
from mlptkeps.providers import evert
from mlptkeps.providers import dailymotion_channels
from mlptkeps.providers import plaintext_provider

epserve = EpisodeServer([
    evert.Evert(),
    plaintext_provider.PlaintextProvider.for_url('https://pastebin.com/raw/uNU30E7k',name='Manual Listing'),
    dailymotion_channels.DailymotionChannelsProvider.parse_from_file('mlptkeps/dailymotion_providers.txt'),
], caching_refresh_rate_minutes=5)

urlpatterns = [
    url(r'^missing$', views.MissingView().get),
    url(r'episodes\.js$', views.EpisodesJsView(epserve).get),
    url(r'\.json$', views.JsonView(epserve).get),
    url(r'^$', views.TableView(epserve).get)
]
