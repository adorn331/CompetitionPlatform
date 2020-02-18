from django.conf.urls import url
from apps.submission.views import submission_create


urlpatterns = [
    url(r'create', submission_create),
    # url(r'update/(?P<id>[0-9]{1,})', competition_update),
]
