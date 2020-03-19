from apps.detector.tasks import hello_site
from django.http.response import HttpResponse
from apps.competition.models import Competition, Participant
from apps.detector.models import Similarity
from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
import csv, codecs


def hello_site_worker(request):
    hello_site.apply_async()
    return HttpResponse("task sent to site_worker.")


@login_required(login_url='/authenz/login')
def list_detector(request):
    user = request.user
    if request.method == 'GET':
        # todo 分页
        username = request.user.username
        competition_list = Competition.objects.all().order_by('-created_time')

        domain = settings.COMPETITIONPLATFORM_SITE_DOMAIN

        return render(request, 'detector/list_detector.html', locals())


@login_required(login_url='/authenz/login')
def plagiarism_detail(request, cid):
    user = request.user
    domain = settings.COMPETITIONPLATFORM_SITE_DOMAIN
    competition = Competition.objects.get(pk=cid)

    threshold = request.GET.get('threshold', 90)
    similarity_records = Similarity.objects.filter(competition=competition, percentage__gt=threshold)

    participant_num = Participant.objects.filter(competition=competition, uploaded_submission__bundle__isnull=False).count()
    total_compare_times = participant_num * (participant_num - 1) / 2
    print(f'total:{total_compare_times}')
    from django.db.models import Count
    current_compared = Similarity.objects.filter(competition=competition).values('src_submission', 'dest_submission').annotate(filecount=Count('src_file')).count()
    print(f'done:{current_compared}')

    percentage_already_compared = (current_compared / total_compare_times) * 100

    if not competition:
        return HttpResponse('<h1>404</h1>')  # todo
    return render(request, 'detector/plagiarism_detail.html', locals())