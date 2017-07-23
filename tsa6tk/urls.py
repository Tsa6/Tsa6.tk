from django.conf.urls import url
from django.conf.urls import include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^(?:webapps/)?mlptkeps/?', include('mlptkeps.urls')),
    url(r'^(?:webapps/)?avoidsafari/?', include('avoidsafari.urls')),
]

handler404 = 'tsa6tk.errors.handle404'