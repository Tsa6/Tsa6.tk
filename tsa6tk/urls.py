from django.conf.urls import url
from django.conf.urls import include
from django.contrib import admin

urlpatterns = [
    url(r'^mlptkeps/?', include('mlptkeps.urls'))
]
