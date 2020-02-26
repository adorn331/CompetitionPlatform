from django.conf.urls import url
from apps.competition.views.competition import competition_create, competition_list_admin, \
    competition_delete, competition_detail, competition_update, competition_list_submission
from apps.competition.views.participants import participant_list, participant_delete, \
    participant_create, participant_update, tmp, get_participants_csv


urlpatterns = [
    # Participants url
    # todo why url改成/participant/list的形式引入static就会出错？
    url(r'(?P<cid>[0-9]{1,})/participants-list', participant_list, name='participant_list'),
    url(r'(?P<cid>[0-9]{1,})/participants-create', participant_create, name='participant_create'),
    url(r'(?P<cid>[0-9]{1,})/participant-(?P<pid>[0-9]{1,})-delete', participant_delete, name='participant_delete'),
    url(r'(?P<cid>[0-9]{1,})/participant-(?P<pid>[0-9]{1,})-update', participant_update, name='participant_update'),
    url(r'(?P<cid>[0-9]{1,})/participants-csv', get_participants_csv, name='get_participants_csv'),
    url(r'tmp', tmp, name='tmp'),

    # Competition url
    url(r'create', competition_create, name='competition_create'),
    url(r'list-admin', competition_list_admin),
    url(r'list-submission', competition_list_submission, name='competition_list_submission'),
    url(r'(?P<cid>[0-9]{1,})/delete', competition_delete, name='competition_delete'),
    url(r'(?P<cid>[0-9]{1,})/detail', competition_detail, name='competition_detail'),
    url(r'(?P<cid>[0-9]{1,})/update', competition_update, name='competition_update'),

]
