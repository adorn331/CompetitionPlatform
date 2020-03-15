from django.conf.urls import url
from apps.submission.views import submission_create, download_all_submission, compare_to_manual_collected


urlpatterns = [
    url(r'create', submission_create),
    url(r'download-(?P<cid>[0-9]{1,})-all-submissions', download_all_submission, name='download_all_submission'),
    url(r'compare-to-manual-collected-submissions-(?P<cid>[0-9]{1,})', compare_to_manual_collected, name='compare_to_manual_collected'),
]
