from apps.competition.models import Competition
from django.http.response import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import traceback
from apps.submission.models import Submission
from apps.competition.models import Competition, Participant
import random


# todo
def _get_filtered_stuff(origin_bundle):
    return origin_bundle


def _verify_bundle(bundle):
    return random.choices([True, False])


# todo 安全性？
def submission_create(request):
    if request.method == "POST":
        print('*' * 10)
        print(request.GET)
        print(request.POST)
        print('*' * 10)

        pid = request.GET['pid']
        cname = request.GET['cname']
        bundle = request.FILES['file']

        submission = Submission()
        submission.competition = Competition.objects.get(name=cname)
        submission.participant = Participant.objects.get(pid=pid)
        submission.bundle = bundle
        filter_bundle = _get_filtered_stuff(bundle)
        submission.filtered_bundle = filter_bundle
        valid = _verify_bundle(filter_bundle)
        submission.status = '合法' if valid else '不合法'
        submission.save()

        return HttpResponse('200')  #todo
    else:
        return HttpResponse('404')  #todo