from django.conf.urls import url
from apps.competition.views.competition import competition_create, competition_list_admin, \
    competition_delete, competition_detail, competition_update, competition_list_submission
from apps.competition.views.participants import participant_list, participant_delete


urlpatterns = [
    # Participants url

    url(r'(?P<id>[0-9]{1,})/participants-list', participant_list, name='participant_list'), #todo why url改成/participant/list就会出错？
    url(r'(?P<cid>[0-9]{1,})/participant/(?P<pid>[0-9]{1,})/delete', participant_delete, name='participant_delete'),
    # todo url为 participants-<id>-update & delete

    # Competition url
    url(r'create', competition_create, name='competition_create'),
    url(r'list-admin', competition_list_admin),
    url(r'list-submission', competition_list_submission, name='competition_list_submission'),
    url(r'(?P<id>[0-9]{1,})/delete', competition_delete, name='competition_delete'),
    url(r'(?P<id>[0-9]{1,})/detail', competition_detail, name='competition_detail'),
    url(r'(?P<id>[0-9]{1,})/update', competition_update, name='competition_update'),

]
