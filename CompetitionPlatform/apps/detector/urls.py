from django.conf.urls import url
from apps.detector.views import hello_site_worker


urlpatterns = [
    url(r'site-worker/', hello_site_worker),      # example usage of celery
]
