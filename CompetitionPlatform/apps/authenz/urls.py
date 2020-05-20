from django.conf.urls import url
from .views import user_register, user_login, user_logout, activate

urlpatterns = [
    url(r'register', user_register),  # 注册
    url(r'login', user_login),  # 登陆
    url(r'logout', user_logout),  # 注销
    url(r'activate/', activate),    # 激活账号
]
