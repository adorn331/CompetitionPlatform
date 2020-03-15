from django.conf.urls import url
from apps.statistics.views import list_statistics, attendance_statistics, completion_statistics


urlpatterns = [
    url(r'list-statistics', list_statistics, name='list_statistics'),
    url(r'(?P<cid>[0-9]{1,})/attendance-statistics', attendance_statistics, name='attendance_statistics'),
    url(r'(?P<cid>[0-9]{1,})/completion-statistics', completion_statistics, name='completion_statistics'),
]
