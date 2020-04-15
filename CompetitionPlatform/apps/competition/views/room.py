from apps.competition.models import Competition, Room
from django.http.response import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import traceback
from apps.competition.utils import parse_participants, parse_standard_from_bundle, parse_hosts
import zipfile
from apps.submission.utils import flatten_dir_structure
from apps.submission.models import Submission
from django.conf import settings
from django.core.paginator import Paginator
from django.urls import reverse
from apps.competition.utils import parse_room_layout


@login_required(login_url='/authenz/login')
def room_list(request):
    user = request.user
    if request.method == 'GET':
        username = request.user.username
        room_list = Room.objects.all().order_by('name')
        paginator = Paginator(room_list, 5)
        page = request.GET.get('page')
        rooms = paginator.get_page(page)
        return render(request, 'room/list.html', locals())


@login_required(login_url='/authenz/login')
def room_delete(request, rid):
    user = request.user
    room_instance = Room.objects.get(pk=rid)
    if room_instance:
        room_instance.delete()
    return redirect(reverse('room_list'))


@login_required(login_url='/authenz/login')
def room_create(request):
    user = request.user

    if request.method == 'POST':
        try:
            name = request.POST['name']

            room = Room()
            room.name = name

            matrix_file = request.FILES.get('matrix_file')
            room.layout_matrix = parse_room_layout(matrix_file)

            room.save()

            return redirect(reverse('room_list'))

        except Exception as e:
            traceback.print_exc()
            return HttpResponse('Internal error:' + str(e))

    elif request.method == 'GET':
        return render(request, 'room/create.html', locals())


@login_required(login_url='/authenz/login')
def room_update(request, rid):
    user = request.user

    if request.method == 'POST':
        try:
            name = request.POST['name']

            room = Room.objects.get(pk=rid)
            matrix_file = request.FILES.get('matrix_file')
            if matrix_file:
                room.layout_matrix = parse_room_layout(matrix_file)
            room.save()

            return redirect(reverse('room_list'))

        except Exception as e:
            traceback.print_exc()
            return HttpResponse('Internal error:' + str(e))

    elif request.method == 'GET':
        return render(request, 'room/update.html', locals())