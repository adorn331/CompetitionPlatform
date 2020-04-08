from apps.submission.models import Submission
from apps.competition.models import Competition, Participant
from apps.submission.utils import verify_bundle, get_filtered_bundle, get_file_md5, tempdir,\
    flatten_dir_structure, unflatten_dir_structure, get_dir_structure
from io import BytesIO
import os
import zipfile
from django.http import HttpResponse
import json
from apps.detector.utils import inspect_plagiarism
from apps.submission.utils import send_request_to_client


def request_all_submission(request, cid):
    competition = Competition.objects.get(pk=cid)
    blank_host_participants = []
    fail_sent_participants = []
    for p in competition.participants.all():
        if p.host:
            try:
                send_request_to_client(p.host, competition.submission_path, p.pno, competition.name)
            except Exception as e:
                fail_sent_participants.append(p)
        else:
            blank_host_participants.append(p)

    msg = ''
    if len(blank_host_participants) == 0 and len(fail_sent_participants) == 0:
        msg += '<br>' + '全部收集请求发送完毕' + '<br>' * 2

    if len(blank_host_participants) > 0:
        msg += '<br>' + '因为未配置选手主机地址，而未发送收集请求的有：' + '<br>' * 2
        for p in blank_host_participants:
            msg += '&emsp;' * 2 + p.pno + '|' + p.name + '<br>'
        msg += '<br>' + '请尽快前往人员管理页面配置上述选手主机地址！' + '<br>'

    if len(fail_sent_participants) > 0:
        msg += '<br>' + '因为网络原因，而未发送收集请求的有:' + '<br>' * 2
        for p in fail_sent_participants:
            msg += '&emsp;' * 2 + p.pno + '|' + p.name + '<br>'
        msg += '<br>' + '请检查上述选手机器上是否开启客户端，以及网络是否正确联通！' +'<br>'

    resp = {
        'code': '200',
        'msg': msg
    }

    return HttpResponse(json.dumps(resp), content_type="application/json", status=200)


def request_single_submission(request, cid, pid):
    print('!!!!!!')
    competition = Competition.objects.get(pk=cid)
    p = Participant.objects.get(pk=pid)
    if p.host:
        try:
            send_request_to_client(p.host, competition.submission_path, p.pno, competition.name)
            resp = {
                'code': '200',
                'msg': '发送成功'
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            resp = {
                'code': '400',
                'msg': '因网络原因，请求失败！请检查上述选手机器上是否开启客户端，以及网络是否正确联通！'
            }

        return HttpResponse(json.dumps(resp), content_type="application/json", status=200)

    else:
        resp = {
            'code': '400',
            'msg': '选手主机地址未配置！请尽快前往比赛的人员管理页面配置！'
        }

        return HttpResponse(json.dumps(resp), content_type="application/json", status=200)


def submission_create(request):
    if request.method == "POST":

        pno = request.GET['pno']
        cname = request.GET['cname']
        bundle = request.FILES['file']

        # ensure the transfer correctly
        client_md5 = request.GET.get('md5', '')

        print(pno, cname, bundle.name, client_md5)
        print(get_file_md5(bundle))
        if client_md5:
            if get_file_md5(bundle) != client_md5:
                return HttpResponse('MD5 not match!', status=400)

        submission = Submission()
        participant = Participant.objects.get(pno=pno, competition__name=cname)
        for previous_sub in participant.uploaded_submission.all(): # cover the previous uploaded submission
            previous_sub.delete()
        submission.participant = participant
        submission.bundle = bundle
        # submission.save()

        submission.valid = verify_bundle(submission, bundle)
        # submission.save()

        get_filtered_bundle(submission, bundle)

        competition = Competition.objects.get(name=cname)
        inspect_plagiarism(competition, submission)

        response = HttpResponse('200', status=200)
        response['Access-Control-Allow-Origin'] = '*' # allow CORS
        return response
    else:
        response = HttpResponse('404 Not Found.', status=404)
        response['Access-Control-Allow-Origin'] = '*'
        return response


def download_all_submission(request, cid):
    competition = Competition.objects.get(pk=cid)

    # Files (local path) to put in the .zip
    submission_list = []
    for p in competition.participants.all():
        submission = Submission.objects.filter(participant=p).first()
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


def compare_to_manual_collected(request, cid):
    msg = ''

    try:
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
            for item in os.listdir(uploaded_dir):
                submission_zip_path = os.path.join(uploaded_dir, item)
                zip_ref = zipfile.ZipFile(submission_zip_path)
                zip_ref.extractall(path=uploaded_dir)
                os.remove(submission_zip_path)

            # unzip each submission from client to collected_dir
            collected_dir = os.path.join(tmpdir, 'collected')
            os.makedirs(collected_dir, exist_ok=True)
            for p in competition.participants.all():
                submission = Submission.objects.filter(participant=p).first()
                if submission:
                    zip_ref = zipfile.ZipFile(submission.bundle.path)
                    zip_ref.extractall(path=collected_dir)

            # star compare and get the result
            uploaded_set = set(flatten_dir_structure(get_dir_structure(uploaded_dir)))
            collected_set = set(flatten_dir_structure(get_dir_structure(collected_dir)))

            diff_set1 = uploaded_set.difference(collected_set)
            if len(diff_set1) > 0:
                msg += '<br>' + '手工收集到而服务器未收集到的文件有:' + '<br>' * 2
                for i in sorted(diff_set1):
                    msg += '&emsp;' * 2 + i + '<br>'

            diff_set2 = collected_set.difference(uploaded_set)
            if len(diff_set2) > 0:
                msg += '<br>' + '服务器收集到而手工未收集到的文件有:' + '<br>' * 2
                for i in sorted(diff_set2):
                    msg += '&emsp;' * 2 + i + '<br>'

            if len(diff_set1) == 0 and len(diff_set2) == 0:
                msg += '<br>' * 8 + '手工收集的提交和服务器收集到的提交相同！'

        resp = {
            'code': '200',
            'msg': msg
        }
        return HttpResponse(json.dumps(resp), content_type="application/json", status=200)

    except Exception:
        msg = '<br>' * 8 + '接口异常，请检查是否所有选手提交都放置一个文件夹内再压缩上传！'
        resp = {
            'code': '200',
            'msg': msg
        }
        return HttpResponse(json.dumps(resp), content_type="application/json", status=200)
