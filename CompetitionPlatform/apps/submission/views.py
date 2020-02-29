from django.http.response import HttpResponse
from apps.submission.models import Submission
from apps.competition.models import Competition, Participant
from apps.submission.utils import verify_bundle, get_filtered_bundle
from io import BytesIO
import os
import zipfile
from django.http import HttpResponse


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
        # submission.save()

        submission.valid = verify_bundle(submission, bundle)
        # submission.save()

        get_filtered_bundle(submission, bundle)

        return HttpResponse('200', status=200)
    else:
        return HttpResponse('404 Not Found.', status=404)


def submission_download_all(request, cid):
    competition = Competition.objects.get(pk=cid)

    # Files (local path) to put in the .zip
    submission_list = []
    for p in competition.participants.all():
        submission = Submission.objects.filter(competition=competition, participant=p).first()
        if submission:
            print(submission.bundle.path)
            submission_list.append(submission.bundle.path)

    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    zip_subdir = f"{competition.name}_all_sub"
    zip_filename = f"{zip_subdir}.zip"

    # Open BytesIO to grab in-memory ZIP contents
    s = BytesIO()

    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in submission_list:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)

        # Add file, at correct path
        zf.write(fpath, zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), content_type='application/zip')
    # ..and correct content-disposition
    resp['Content-Disposition'] = f'attachment; filename={zip_filename}'

    return resp
