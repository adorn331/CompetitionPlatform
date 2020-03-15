from apps.detector.tasks import hello_site
from django.http.response import HttpResponse


def hello_site_worker(request):
    hello_site.apply_async()
    return HttpResponse("task sent to site_worker.")