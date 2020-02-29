from django.conf.urls import url
from apps.submission.views import submission_create, submission_download_all


urlpatterns = [
    url(r'create', submission_create),
    url(r'download-(?P<cid>[0-9]{1,})-all-submission', submission_download_all, name='submission_download_all'),
]
