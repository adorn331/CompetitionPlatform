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
from django.core.paginator import Paginator
from apps.competition.utils import turn_0_1_to_num_matrix
import json


@login_required(login_url='/authenz/login')
def summary_graph(request, cid):
    color_mapping = {
        '已提交且符合规范': '#2ECC71',
        '提交失败': '#E74C3C',
        '已提交': '#F7DC6F',
        '': '#C8C8C8'
    }
    user = request.user
    domain = settings.COMPETITIONPLATFORM_SITE_DOMAIN
    if request.method == 'GET':
        username = request.user.username
        competition = Competition.objects.get(pk=cid)
        layout_str = competition.room_layout.layout_matrix
        layout = json.loads(layout_str)
        print(layout)
        turn_0_1_to_num_matrix(layout)
        print(layout)

        participant_grid = layout.copy()
        for i in range(len(participant_grid)):
            for j in range(len(participant_grid[0])):
                p = Participant.objects.filter(competition=competition, position=participant_grid[i][j]).first()
                if participant_grid[i][j] != 0 and p:
                    if p.uploaded_submission.count() > 0:
                        p.color = color_mapping[p.uploaded_submission.first().status.split(':')[0]]
                    else:
                        p.color = color_mapping['']
                    participant_grid[i][j] = p
                else:
                    p = Participant()
                    p.position = participant_grid[i][j]
                    p.color = '#000000'
                    participant_grid[i][j] = p
        print(participant_grid)
        max_col = len(participant_grid[0])
        col_range = range(max_col)
        percentage_width_percol = 100 / max_col
        print(participant_grid)


        # username = request.user.username
        # participants = Competition.objects.get(pk=cid).participants.all().order_by('position')
        # participant_grid = []
        # max_col = 0
        # if participants:
        #     grid_row = - 1
        #     for p in participants:
        #         if not p.position:
        #             p.position = '1-1'
        #         cur_row, cur_col = parse_position(p.position)
        #         max_col = max(cur_col, max_col)
        #         if cur_row - 1 > grid_row:
        #             participant_grid.append([])
        #             grid_row += 1
        #         participant_grid[grid_row].append(p)
        #
        #         if p.uploaded_submission.count() > 0:
        #             p.color = color_mapping[p.uploaded_submission.first().status.split(':')[0]]
        #         else:
        #             p.color = color_mapping['']
        #
        # col_range = range(max_col)
        # percentage_width_percol = 100 / max_col
        # print(participant_grid)

        return render(request, 'statistics/summary_graph.html', locals())

@login_required(login_url='/authenz/login')
def list_statistics(request):
    user = request.user
    if request.method == 'GET':
        username = request.user.username
        competition_list = Competition.objects.all().order_by('-created_time')
        paginator = Paginator(competition_list, 5)
        page = request.GET.get('page')
        competitions = paginator.get_page(page)

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
    participants_list = competition.participants.all().order_by('pno')
    paginator = Paginator(participants_list, 13)
    page = request.GET.get('page')
    participants = paginator.get_page(page)

    for p in participants:
        p.submission = Submission.objects.filter(participant=p).first()
        if p.submission:
            # p.submission.status = '已提交且符合规范' if p.submission.valid else '已提交但不符合规范'

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
            # p.submission.status = '已提交且符合规范' if p.submission.valid else '已提交但不符合规范'

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

        writer.writerow([p.pno, p.name, p.submission.status, p.display_missing])

    return response