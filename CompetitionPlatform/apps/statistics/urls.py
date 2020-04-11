from django.conf.urls import url
from apps.statistics.views import list_statistics, attendance_statistics, completion_statistics,\
    get_attended_participant_csv, get_unattended_participant_csv, get_compeltion_csv, summary_graph


urlpatterns = [
    url(r'list-statistics', list_statistics, name='list_statistics'),
    url(r'(?P<cid>[0-9]{1,})/summary_graph', summary_graph, name='summary_graph'),
    url(r'(?P<cid>[0-9]{1,})/attendance-statistics', attendance_statistics, name='attendance_statistics'),
    url(r'(?P<cid>[0-9]{1,})/completion-statistics', completion_statistics, name='completion_statistics'),
    url(r'(?P<cid>[0-9]{1,})/attended-participant-csv', get_attended_participant_csv, name='get_attended_participant_csv'),
    url(r'(?P<cid>[0-9]{1,})/unattended-participant-csv', get_unattended_participant_csv, name='get_unattended_participant_csv'),
    url(r'(?P<cid>[0-9]{1,})/compeltion-csv', get_compeltion_csv, name='get_compeltion_csv'),
]
