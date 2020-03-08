from django.core.mail import send_mail
from apps.authenz.models import User
from django.http.response import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.shortcuts import redirect
import re
import traceback
from apps.authenz.token import token_manager
from django.conf import settings


def activate(request):
    token = request.GET['token']
    user_id, errmsg = token_manager.confirm_validate_token(token)
    if errmsg:
        if errmsg == '激活码已过期':
            user_id = token_manager.get_validate_token(token)
            user = User.objects.get(pk=user_id)
            user.delete()
        return HttpResponse(errmsg)

    user = User.objects.get(pk=user_id)
    if not user:
        error = '所激活的用户不存在'
        return render(request, 'authenz/login.html', locals())
    user.isactivate = True
    user.save()

    msg = '用户激活成功！请登录！'
    return render(request, 'authenz/login.html', locals())


def user_register(request):
    if request.method == 'POST':
        try:
            username = request.POST['username']
            password = request.POST['password']
            password_confirm = request.POST['password_confirm']
            email = request.POST['email']

            if password != password_confirm:
                error = "两次输入的密码不相同"
                return render(request, 'authenz/register.html', locals())

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

            # email validation
            token = token_manager.generate_validate_token(user.id)
            token_url = f'http://{settings.COMPETITIONPLATFORM_SITE_DOMAIN}/authenz/activate?token={token}'
            message = "\n".join([u'{0},欢迎加入竞赛平台管理员'.format(username), u'请访问该链接，完成用户验证:',
                                 token_url])
            send_mail(u'注册用户验证信息', message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
            msg = '已发送验证邮箱，请前往验证后登录！'
            return render(request, 'authenz/login.html', locals())

        except Exception as e:
            traceback.print_exc()
            return HttpResponse('internal error')   # todo pretty
    else:
        return render(request, 'authenz/register.html', locals())


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            if not user.isactivate and settings.NEED_EMAIL_VALIDATION == 'True':
                error = '用户未激活！ 请前往注册邮件点击链接激活！'
                return render(request, 'authenz/login.html', locals())
            login(request, user)  # 登录
            request.session['user'] = username  # 将session信息记录到浏览器
            return redirect('/competition/list-admin')
        else:
            error = 'username or password error!'
            return render(request, 'authenz/login.html', locals())
    else:
        return render(request, 'authenz/login.html')


def user_logout(request):
    try:
        logout(request)

        return redirect('/authenz/login')

    except Exception as e:

        return redirect('/authenz/login')

