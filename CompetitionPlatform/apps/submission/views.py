from django.http.response import HttpResponse
from apps.submission.models import Submission
from apps.competition.models import Competition, Participant
from apps.submission.utils import verify_bundle, get_filtered_bundle


# todo 安全性？
def submission_create(request):
    if request.method == "POST":

        pno = request.GET['pno']
        cname = request.GET['cname']
        bundle = request.FILES['file']

        submission = Submission()
        submission.competition = Competition.objects.get(name=cname)
        submission.participant = Participant.objects.get(pno=pno)
        submission.bundle = bundle

        valid = verify_bundle(submission, bundle)
        submission.status = '已提交且符合规范' if valid else '已提交但不符合规范'
        submission.save()

        get_filtered_bundle(submission, bundle)

        print(submission.bundle)
        print(submission.filtered_bundle)
        return HttpResponse('200', status=200)
    else:
        return HttpResponse('404 Not Found.', status=404)