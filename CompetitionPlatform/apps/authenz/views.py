from apps.authenz.models import User
from apps.authenz.forms import UserForm
from django.http.response import HttpResponse
import json
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.shortcuts import redirect


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
    # if request.session.get('is_login', None):  # 不允许重复登录
    #     return redirect('/index/')
    # if request.method == 'POST':
    #     login_form = UserForm(request.POST)
    #     message = '请检查填写的信息！'
    #     if login_form.is_valid():
    #         username = login_form.cleaned_data.get('username')
    #         password = login_form.cleaned_data.get('password')
    #         temper_user = User()
    #         try:
    #             user = User.objects.get(username=username)
    #         except:
    #             message = '用户不存在！'
    #             return render(request, 'authenz/login.html', locals())
    #         user = authenticate(request, username=username, password=password)
    #         if user:
    #             login(request, user)
    #         else:
    #             message = '密码不正确！'
    #             return render(request, 'authenz/login.html', locals())
    #     else:
    #         return render(request, 'authenz/login.html', locals())
    # else:
    #     login_form = UserForm()
    #     return render(request, 'authenz/login.html', locals())

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)  # 登录
            request.session['user'] = username  # 将session信息记录到浏览器
            return HttpResponse('login success!')
        else:
            return render(request, 'authenz/login.html', {'error': 'username or password error!'})
    else:
        return render(request, 'authenz/login.html')

    # if request.method == "POST":
    #     try:
    #         username = request.POST['username']
    #         password = request.POST['password']
    #
    #         user = authenticate(request, username=username, password=password)
    #         login(request, user)
    #
    #         return HttpResponse(content_type="application/json", status=200)
    #
    #     except Exception as e:
    #
    #         return HttpResponse(content_type="application/json", status=500)


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
