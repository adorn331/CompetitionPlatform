from apps.competition.models import Competition, Participant
from django.http.response import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import traceback
from apps.competition.utils import parse_participants, parse_standard_from_bundle
import zipfile
from apps.submission.utils import flatten_dir_structure


@login_required(login_url='/authenz/login')
def competition_create(request):
    user = request.user
    if request.method == 'POST':
        try:
            name = request.POST['name']
            description = request.POST['description']
            file_list = request.FILES.getlist('file')

            # save basic info
            competition = Competition()
            competition.name = name
            competition.description = description
            competition.submission_standard = {}
            cid = competition.save()

            # handle the files uploaded.
            for f in file_list:
                # config participants from csv uploaded.
                if f.name == 'namelist.csv':
                    parse_participants(f, competition)

                else:
                    print('$$$$$$$$$$')
                    print(zipfile.is_zipfile(f))
                    # parse standard bundle
                    submission_standard = parse_standard_from_bundle(f)
                    competition.submission_standard = submission_standard

            competition.save()

            return redirect('/competition/list-admin')

        except Exception as e:
            traceback.print_exc()
            return HttpResponse('Internal error:' + str(e))
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
        if p.submission:
            p.submission.status = '已提交且符合规范' if p.submission.valid else '已提交但不符合规范'
            p.display_bundle = '已提交文件<br>'
            if p.submission.bundle_structure:
                file_list = flatten_dir_structure(p.submission.bundle_structure)
                for i in file_list:
                    p.display_bundle = p.display_bundle + i + '<br>'

            if p.submission.missing_files:
                p.display_missing = '<br>缺失文件<br>'
                file_list = flatten_dir_structure(p.submission.missing_files)
                for i in file_list:
                    p.display_missing = p.display_missing + i + '<br>'

    # domain = settings.COMPETITIONPLATFORM_SITE_DOMAIN
    # # # todo change back!!!!!!
    domain = '127.0.0.1'

    if not competition:
        return HttpResponse('<h1>404</h1>')  # todo
    return render(request, 'competition/detail.html', locals())


@login_required(login_url='/authenz/login')
def competition_delete(request, cid):
    user = request.user
    # todo front end add del confirm.
    comp_instance = Competition.objects.get(pk=cid)
    comp_instance.participants.all().delete()
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
        file_list = request.FILES.getlist('file')

        competition.name = name
        competition.description = description
        competition.save()

        # handle the files uploaded.
        for f in file_list:
            # config participants from csv uploaded.
            if f.name == 'namelist.csv':
                parse_participants(f, competition)

            else:
                # parse standard bundle
                submission_standard = parse_standard_from_bundle(f)
                competition.submission_standard = submission_standard

        competition.save()
        return redirect('/competition/list-admin')

    elif request.method == 'GET':
        return render(request, 'competition/update.html', locals())
