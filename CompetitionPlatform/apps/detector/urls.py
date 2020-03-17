from django.conf.urls import url
from apps.detector.views import hello_site_worker
from apps.detector.views import list_detector, plagiarism_detail


urlpatterns = [
    url(r'site-worker/', hello_site_worker),      # example usage of celery
    url(r'list-detector', list_detector, name='list_detector'),
    url(r'(?P<cid>[0-9]{1,})/plagiarism_detail', plagiarism_detail, name='plagiarism_detail'),
]
