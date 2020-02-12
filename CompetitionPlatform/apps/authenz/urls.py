from django.conf.urls import url
from .views import user_register, user_login, user_logout, query_user

urlpatterns = [
    url(r'register', user_register),
    url(r'login', user_login),
    url(r'logout', user_logout),
    url(r'', query_user),
]
