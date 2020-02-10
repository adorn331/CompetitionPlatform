from apps.users.models import User
from django.http.response import HttpResponse
import json
from django.contrib.auth import authenticate, login, logout


def user_register(request):
    if request.method == 'POST':
        try:
            username = request.POST['username']
            password = request.POST['password']
            email = request.POST.get['email']

            if User.objects.filter(username=username).exists():
                resp = {
                    'code': 401,
                    'msg': "user name exist!"
                }
                return HttpResponse(json.dumps(resp), content_type="application/json", status=400)

            if User.objects.filter(email=email).exists():
                resp = {
                    'code': 402,
                    'msg': "email name exist!"
                }
                return HttpResponse(json.dumps(resp), content_type="application/json", status=400)

            # save the user to db
            user = User()
            user.username = username
            user.set_password(password)
            user.email = email
            user.save()

            return HttpResponse(content_type="application/json", status=200)

        except Exception as e:

            return HttpResponse(content_type="application/json", status=500)


def user_login(request):
    if request.method == "POST":
        try:
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)
            login(request, user)

            return HttpResponse(content_type="application/json", status=200)

        except Exception as e:

            return HttpResponse(content_type="application/json", status=500)


def user_logout(request):
    try:
        logout(request)

        return HttpResponse(content_type="application/json", status=200)

    except Exception as e:

        return HttpResponse(content_type="application/json", status=500)


def query_user(request):
    try:
        if request.user.username == '':
            resp = {
                'code': 403,
                'data': {
                    'islogin': False,
                    'username': ''
                }
            }
            return HttpResponse(json.dumps(resp), content_type="application/json", status=403)
        else:
            resp = {
                'code': 0,
                'data': {
                    'islogin': True,
                    'username': request.user.username
                }
            }
            return HttpResponse(json.dumps(resp), content_type="application/json", status=200)

    except Exception as e:

        return HttpResponse(content_type="application/json", status=500)
