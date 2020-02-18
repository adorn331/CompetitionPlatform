from apps.competition.models import Competition, Participant
from django.http.response import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import traceback
from django.conf import settings
from django.urls import reverse


@login_required(login_url='/authenz/login')
def participant_list(request, id):
    user = request.user
    competition = Competition.objects.get(pk=id)
    participants = competition.participants.all()
    domain = settings.COMPETITIIONPLATFORM_SITE_DOMAIN

    if not competition:
        return HttpResponse('404')  # todo
    return render(request, 'participant/list.html', locals())


@login_required(login_url='/authenz/login')
def participant_delete(request, cid, pid):
    user = request.user
    competition = Competition.objects.get(pk=cid)
    participant = Participant.objects.get(pk=pid)

    if not competition or not participant:
        return HttpResponse('404')  # todo

    participant.delete()
    return redirect(reverse('participant_list', args=(cid, )))