from apps.competition.models import Competition
from django.http.response import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import traceback
from django.conf import settings


def _get_file_and_prase():
    # todo get post file and parse to json
    return {'test': 'test'}


@login_required(login_url='/authenz/login')
def competition_create(request):
    user = request.user
    if request.method == 'POST':
        try:
            name = request.POST['name']
            description = request.POST['description']

            # todo finish the prase from file.
            submission_standard = _get_file_and_prase()
            participants = _get_file_and_prase()
            print('*' * 10)
            print(request.FILES.getlist('file'))
            print('*' * 10)

            competition = Competition()
            competition.name = name
            competition.description = description
            competition.submission_standard = submission_standard
            competition.save()

            return redirect('/competition/list-admin')

        except Exception as e:
            traceback.print_exc()
            return HttpResponse('Internal error:', e)
    elif request.method == 'GET':
        return render(request, 'competition/create.html', locals())


@login_required(login_url='/authenz/login')
def competition_list_admin(request):
    user = request.user
    if request.method == 'GET':
        # todo 分页
        username = request.user.username
        competition_list = Competition.objects.all().order_by('-created_time')
        return render(request, 'competition/list_admin.html', locals())


@login_required(login_url='/authenz/login')
def competition_list_submission(request):
    user = request.user
    if request.method == 'GET':
        # todo 分页
        username = request.user.username
        competition_list = Competition.objects.all().order_by('-created_time')
        return render(request, 'competition/list_submission.html', locals())


@login_required(login_url='/authenz/login')
def competition_detail(request, cid):
    user = request.user
    competition = Competition.objects.get(pk=cid)
    participants = competition.participants.all()

    for p in participants:
        p.submission = p.get_submission(competition)

    # domain = settings.COMPETITIONPLATFORM_SITE_DOMAIN
    # # # todo change back!!!!!!
    domain = '127.0.0.1'

    if not competition:
        return HttpResponse('<h1>404</h1>')  # todo
    return render(request, 'competition/detail.html', locals())


@login_required(login_url='/authenz/login')
def competition_delete(request, cid):
    print('11111')
    user = request.user
    # todo front end add del confirm.
    comp_instance = Competition.objects.get(pk=cid)
    if comp_instance:
        comp_instance.delete()
    return redirect('/competition/list-admin')


@login_required(login_url='/authenz/login')
def competition_update(request, cid):
    user = request.user
    competition = Competition.objects.get(pk=cid)
    if not competition:
        return HttpResponse('404')  # todo

    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        competition.name = name
        competition.description = description
        # todo finish the prase from file if exist.
        competition.save()
        return redirect('/competition/list-admin')

    elif request.method == 'GET':
        return render(request, 'competition/update.html', locals())
