from apps.demo.models import People
from rest_framework import viewsets
from apps.demo.serializers import PeopleSerializer
from django.contrib.auth.mixins import LoginRequiredMixin


class PeopleViewSet(viewsets.ModelViewSet):
    queryset = People.objects.all()
    serializer_class = PeopleSerializer


# from django.http.response import HttpResponse
# from apps.demo.tasks import hello_site
# from celery.app import app_or_default

# example usage of celery
# def hello_site_worker(request):
#     hello_site.apply_async()
#     return HttpResponse("task sent to site_worker.")

# example usage of celery
# def hello_compute_worker(request):
#     app = app_or_default()
#     app.send_task('compute_worker_run', [], queue='compute-worker')
#     return HttpResponse("task sent to compute_worker.")