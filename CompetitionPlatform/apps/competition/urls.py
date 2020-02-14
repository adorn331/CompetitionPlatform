from django.conf.urls import url
from apps.competition.views import whole_competition_view, detail_competition_view


urlpatterns = [
    url(r'^(?P<id>[0-9]{1,})', detail_competition_view),
    url(r'^$', whole_competition_view),
]
