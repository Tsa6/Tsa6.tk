from django.conf.urls import url
from django.conf.urls import include
from django.contrib import admin
from tsa6tk.errors import handle404

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^(?:webapps/)?mlptkeps/?', include('mlptkeps.urls'))
]

handler404 = 'tsa6tk.errors.handle404'