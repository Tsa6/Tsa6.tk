from django.conf.urls import url
from django.conf.urls import include
from django.contrib import admin

urlpatterns = [
    url(r'^(?:webapps/)?mlptkeps/?', include('mlptkeps.urls'))
]
