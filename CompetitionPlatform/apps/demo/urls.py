from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from apps.demo.views import PeopleViewSet
# from apps.demo.views import hello_site_worker, hello_compute_worker

router = DefaultRouter()
router.register(r'people', PeopleViewSet)

urlpatterns = [
    # url(r'site-worker/', hello_site_worker),      # example usage of celery
    # url(r'compute-worker/', hello_compute_worker), # example usage of celery
]

urlpatterns += router.urls
