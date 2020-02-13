from apps.authenz.models import User
from apps.authenz.forms import UserForm
from django.http.response import HttpResponse
import json
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.shortcuts import redirect
import re
import traceback


def user_register(request):
    if request.method == 'POST':
        try:
            username = request.POST['username']
            password = request.POST['password']
            email = request.POST['email']

            user_regex = r'^[0-9a-zA-Z_]{5,}$'
            if not re.match(user_regex, username):
                error = "Invalid user format!"
                return render(request, 'authenz/register.html', locals())

            if len(password) < 7:
                error = "Password can not be less than 7 character"
                return render(request, 'authenz/register.html', locals())

            if User.objects.filter(username=username).exists():
                error = 'username already existed!'
                return render(request, 'authenz/register.html', locals())

            if User.objects.filter(email=email).exists():
                error = 'email already existed!'
                return render(request, 'authenz/register.html', locals())

            # save the user to db
            user = User()
            user.username = username
            user.set_password(password)
            user.email = email
            user.save()

            return redirect('/authenz/login')

        except Exception as e:
            traceback.print_exc()
            return HttpResponse('internal error')
    else:
        return render(request, 'authenz/register.html', locals())


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)  # 登录
            request.session['user'] = username  # 将session信息记录到浏览器
            return HttpResponse('login success!')
        else:
            error = 'username or password error!'
            return render(request, 'authenz/login.html', locals())
    else:
        return render(request, 'authenz/login.html')


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
