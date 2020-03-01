from django.http.response import HttpResponse
from django.shortcuts import redirect

from apps.submission.models import Submission
from apps.competition.models import Competition, Participant
from apps.submission.utils import verify_bundle, get_filtered_bundle, get_file_md5, tempdir, flatten_dir_structure, unflatten_dir_structure, get_dir_structure
from io import BytesIO
import os
import zipfile
from django.http import HttpResponse
import json


# todo 安全性？
def submission_create(request):
    if request.method == "POST":

        pno = request.GET['pno']
        cname = request.GET['cname']
        bundle = request.FILES['file']

        # ensure the transfer correctly
        client_md5 = request.GET.get('md5', '')
        if client_md5:
            if get_file_md5(bundle) != client_md5:
                return HttpResponse('MD5 not match!', status=400)

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


def download_all_submission(request, cid):
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


def compare_submission(request, cid):
    msg = ''

    competition = Competition.objects.get(pk=cid)
    bundle = request.FILES['file']
    with tempdir() as tmpdir:
        # save it and extract
        bundle_zip_path = tmpdir + '/bundle.zip'

        with open(bundle_zip_path, 'wb+') as tmpbundle:
            for chunk in bundle.chunks():
                tmpbundle.write(chunk)

        zip_ref = zipfile.ZipFile(bundle_zip_path)

        # extract the uploaded bundle
        zip_ref.extractall()
        # remove the zip bundle
        os.remove(bundle_zip_path)
        # then leave the unzipped dir as uploaded_dir
        uploaded_dir = os.path.join(tmpdir, os.listdir(tmpdir)[0]) # 这样代表是一个文件夹压缩过来的，例如answers

        # extract every sub zip bundle
        print(os.listdir(uploaded_dir))
        for item in os.listdir(uploaded_dir):
            submission_zip_path = os.path.join(uploaded_dir, item)
            zip_ref = zipfile.ZipFile(submission_zip_path)
            zip_ref.extractall(path=uploaded_dir)
            os.remove(submission_zip_path)
        print(os.listdir(uploaded_dir))

        # unzip each submission from client to collected_dir
        collected_dir = os.path.join(tmpdir, 'collected')
        os.makedirs(collected_dir, exist_ok=True)
        for p in competition.participants.all():
            submission = Submission.objects.filter(competition=competition, participant=p).first()
            if submission:
                zip_ref = zipfile.ZipFile(submission.bundle.path)
                zip_ref.extractall(path=collected_dir)
        print(os.listdir(tmpdir))
        print(os.listdir(collected_dir))

        # star compare and get the result
        print('@@@@@@@@@@@@@@@@@')
        uploaded_set = set(flatten_dir_structure(get_dir_structure(uploaded_dir)))
        collected_set = set(flatten_dir_structure(get_dir_structure(collected_dir)))

        diff_set1 = uploaded_set.difference(collected_set)
        if len(diff_set1) > 0:
            msg += '<br>' + '手工收集到而服务器未收集到的文件有:' + '<br>' * 2
            for i in diff_set1:
                msg += '&emsp;' * 2 + i + '<br>'

        diff_set2 = collected_set.difference(uploaded_set)
        if len(diff_set2) > 0:
            msg += '<br>' + '服务器收集到而手工未收集到的文件有:' + '<br>' * 2
            for i in diff_set2:
                msg += '&emsp;' * 2 + i + '<br>'
            print('@@@@@@@@@@@@@@@@@')

        if len(diff_set1) == 0 and len(diff_set2) == 0:
            msg += '<br>' * 8 + '手工收集的提交和服务器收集到的提交相同！'

    resp = {
        'code': '200',
        'msg': msg
    }
    return HttpResponse(json.dumps(resp), content_type="application/json", status=200)
