from apps.competition.models import Competition
from django.http.response import HttpResponse
import json
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.shortcuts import redirect
import traceback
from django.core import serializers
from django.contrib.auth.decorators import login_required


def _get_file_and_prase():
    # todo get post file and parse to json
    return {'test': 'test'}


@login_required(login_url='/authenz/login')
def whole_competition_view(request):
    if request.method == 'POST':
        try:
            name = request.POST['name']
            description = request.POST['description']
            submission_standard = _get_file_and_prase()

            competition = Competition()
            competition.name = name
            competition.description = description
            competition.submission_standard = submission_standard
            competition.save()

            return HttpResponse('saved!')

        except Exception as e:
            return HttpResponse('internal error:', e)

    elif request.method == 'GET':
        username = request.user.username
        data = serializers.serialize("json", Competition.objects.all(), fields=('name', 'description', 'created_time'))
        # return HttpResponse(data)
        return render(request, 'competition/list.html', locals())


@login_required(login_url='/authenz/login')
def detail_competition_view(request, id):
    comp_instance = Competition.objects.get(pk=id)
    if not comp_instance:
        return HttpResponse('404')  # todo

    if request.method == 'GET':
        data = serializers.serialize("json", Competition.objects.filter(pk=id))
        return HttpResponse(data)

    elif request.method == 'DELETE':
        return HttpResponse(id)

