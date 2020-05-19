from apps.competition.models import Competition, Room
from django.http.response import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import traceback
from django.core.paginator import Paginator
from django.urls import reverse
from apps.competition.utils import parse_room_layout
import json


@login_required(login_url='/authenz/login')
def room_list(request):
    user = request.user
    if request.method == 'GET':
        username = request.user.username
        room_list = Room.objects.all().order_by('name')
        paginator = Paginator(room_list, 5)
        page = request.GET.get('page')
        rooms = paginator.get_page(page)
        for r in rooms:
            r.display_layout = ''
            for line in json.loads(r.layout_matrix):
                r.display_layout += str(line)
                r.display_layout += '</br>'
        return render(request, 'room/list.html', locals())


@login_required(login_url='/authenz/login')
def room_delete(request, rid):
    from django.db.models.deletion import ProtectedError
    try:
        user = request.user
        room_instance = Room.objects.get(pk=rid)
        if room_instance:
            room_instance.delete()
    except ProtectedError as e:
        return HttpResponse('考场已被其他比赛引用，删除失败！需要删除请先删除比赛！')
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
            return HttpResponse('格式解析错误！请参照参考0-1矩阵文本文件来编写布局矩阵！')

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
            return HttpResponse('格式解析错误！请参照参考0-1矩阵文本文件来编写布局矩阵！')

    elif request.method == 'GET':
        room = Room.objects.get(pk=rid)
        return render(request, 'room/update.html', locals())