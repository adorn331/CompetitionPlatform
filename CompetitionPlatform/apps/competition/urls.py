from django.conf.urls import url
from apps.competition.views import competition_create, competition_list_admin, \
    competition_delete, competition_detail, competition_update, competition_list_submission


urlpatterns = [
    url(r'create', competition_create),
    url(r'list-admin', competition_list_admin),
    url(r'list-submission', competition_list_submission),
    url(r'delete/(?P<id>[0-9]{1,})', competition_delete),
    url(r'detail/(?P<id>[0-9]{1,})', competition_detail),
    url(r'update/(?P<id>[0-9]{1,})', competition_update),
]
