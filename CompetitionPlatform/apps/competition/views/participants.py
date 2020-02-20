from apps.competition.models import Competition, Participant
from django.http.response import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import traceback
from django.conf import settings
from django.urls import reverse


@login_required(login_url='/authenz/login')
def participant_list(request, cid):
    user = request.user
    competition = Competition.objects.get(pk=cid)
    participants = competition.participants.all()
    domain = settings.COMPETITIONPLATFORM_SITE_DOMAIN

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

    competition.participants.remove(participant)
    return redirect(reverse('participant_list', args=(cid, )))


@login_required(login_url='/authenz/login')
def participant_create(request, cid):
    user = request.user
    competition = Competition.objects.get(pk=cid)

    if request.method == 'POST':
        try:
            name = request.POST['name']
            pid = request.POST['pid']
            gender = request.POST.get('gender')

            participant = Participant()
            participant.name = name
            participant.pid = pid
            participant.gender = gender
            participant.save()

            competition.participants.add(participant)

            return redirect(reverse('participant_list', args=(cid, )))

        except Exception as e:
            traceback.print_exc()
            return HttpResponse('Internal error:', e)

    elif request.method == 'GET':
        return render(request, 'participant/create.html', locals())


@login_required(login_url='/authenz/login')
def participant_update(request, cid, pid):
    user = request.user
    competition = Competition.objects.get(pk=cid)
    participant = Participant.objects.get(pk=pid)

    if not competition or not participant:
        return HttpResponse('404')  # todo

    if request.method == 'POST':
        name = request.POST['name']
        pid = request.POST['pid']
        gender = request.POST.get('gender')
        participant.name = name
        participant.pid = pid
        participant.gender = gender
        participant.save()
        return redirect(reverse('participant_list', args=(cid, )))

    elif request.method == 'GET':
        return render(request, 'participant/update.html', locals())


def tmp(request):
    return render(request, 'participant/tmp.html', locals())