from django.conf.urls import url
from apps.submission.views import submission_create, download_all_submission, compare_submission


urlpatterns = [
    url(r'create', submission_create),
    url(r'download-(?P<cid>[0-9]{1,})-all-submissions', download_all_submission, name='download_all_submission'),
    url(r'compare-(?P<cid>[0-9]{1,})-submissions', compare_submission, name='compare_submission'),
]
