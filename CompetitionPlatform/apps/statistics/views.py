from apps.competition.models import Competition, Participant
from django.http.response import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import traceback
from apps.competition.utils import parse_participants, parse_standard_from_bundle
import zipfile
from apps.submission.utils import flatten_dir_structure
from apps.submission.models import Submission
from django.conf import settings
import csv, codecs


@login_required(login_url='/authenz/login')
def list_statistics(request):
    user = request.user
    if request.method == 'GET':
        # todo 分页
        username = request.user.username
        competition_list = Competition.objects.all().order_by('-created_time')

        domain = settings.COMPETITIONPLATFORM_SITE_DOMAIN

        return render(request, 'statistics/list_statistics.html', locals())


@login_required(login_url='/authenz/login')
def attendance_statistics(request, cid):
    user = request.user
    competition = Competition.objects.get(pk=cid)
    participants = competition.participants.all().order_by('pno')
    attended_participants = []
    unattended_participants = []
    for p in participants:
        if p.uploaded_submission.count() != 0:
            attended_participants.append(p)
        else:
            unattended_participants.append(p)

    domain = settings.COMPETITIONPLATFORM_SITE_DOMAIN

    if not competition:
        return HttpResponse('404')  # todo
    return render(request, 'statistics/attendence_statistics.html', locals())


@login_required(login_url='/authenz/login')
def completion_statistics(request, cid):
    user = request.user
    competition = Competition.objects.get(pk=cid)
    participants = competition.participants.all().order_by('pno')

    for p in participants:
        p.submission = Submission.objects.filter(participant=p).first()
        if p.submission:
            p.submission.status = '已提交且符合规范' if p.submission.valid else '已提交但不符合规范'

            p.display_missing = ''
            if p.submission.missing_files:
                file_list = flatten_dir_structure(p.submission.missing_files)
                for i in file_list:
                    p.display_missing = p.display_missing + i.split('/')[-1] + ' ｜ '
                p.display_missing = p.display_missing[:-2]
        else:
            p.display_missing = ''
            if competition.submission_standard:
                file_list = flatten_dir_structure(competition.submission_standard)
                for i in file_list:
                    p.display_missing = p.display_missing + i.split('/')[-1] + ' ｜ '
                p.display_missing = p.display_missing[:-2]

    domain = settings.COMPETITIONPLATFORM_SITE_DOMAIN

    if not competition:
        return HttpResponse('<h1>404</h1>')  # todo
    return render(request, 'statistics/completion_statistics.html', locals())


@login_required(login_url='/authenz/login')
def get_attended_participant_csv(request, cid):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="namelist.csv"'
    response.write(codecs.BOM_UTF8)  # todo figure out why?
    writer = csv.writer(response)


    competition = Competition.objects.get(pk=cid)
    participants = competition.participants.all().order_by('pno')
    attended_participants = []
    unattended_participants = []
    for p in participants:
        if p.uploaded_submission.count() != 0:
            attended_participants.append(p)
        else:
            unattended_participants.append(p)

    for p in attended_participants:
        writer.writerow([p.pno, p.province, p.name, p.id_num, p.school, p.grade])

    return response


@login_required(login_url='/authenz/login')
def get_unattended_participant_csv(request, cid):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="namelist.csv"'
    response.write(codecs.BOM_UTF8) # todo figure out why?
    writer = csv.writer(response)

    competition = Competition.objects.get(pk=cid)
    participants = competition.participants.all().order_by('pno')
    attended_participants = []
    unattended_participants = []
    for p in participants:
        if p.uploaded_submission.count() != 0:
            attended_participants.append(p)
        else:
            unattended_participants.append(p)

    for p in unattended_participants:
        print([p.pno, p.province, p.name, p.id_num, p.school, p.grade])
        writer.writerow([p.pno, p.province, p.name, p.id_num, p.school, p.grade])

    return response


@login_required(login_url='/authenz/login')
def get_compeltion_csv(request, cid):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="compeltion_statistic.csv"'
    response.write(codecs.BOM_UTF8) # todo figure out why?
    writer = csv.writer(response)

    competition = Competition.objects.get(pk=cid)
    participants = competition.participants.all().order_by('pno')

    writer.writerow(['考号', '姓名', '状态', '未完成题目'])

    for p in participants:
        p.submission = Submission.objects.filter(participant=p).first()
        if p.submission:
            p.submission.status = '已提交且符合规范' if p.submission.valid else '已提交但不符合规范'

            p.display_missing = ''
            if p.submission.missing_files:
                file_list = flatten_dir_structure(p.submission.missing_files)
                for i in file_list:
                    p.display_missing = p.display_missing + i.split('/')[-1] + ' ｜ '
                p.display_missing = p.display_missing[:-2]
        else:
            p.display_missing = ''
            if competition.submission_standard:
                file_list = flatten_dir_structure(competition.submission_standard)
                for i in file_list:
                    p.display_missing = p.display_missing + i.split('/')[-1] + ' ｜ '
                p.display_missing = p.display_missing[:-2]

        writer.writerow([p.pno, p.name, p.submission.status if p.submission else '未提交', p.display_missing])

    return response