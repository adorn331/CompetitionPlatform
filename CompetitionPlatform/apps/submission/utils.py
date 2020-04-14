from apps.competition.utils import tempdir, get_dir_structure, flatten_dir_structure, unflatten_dir_structure
import zipfile, os, shutil
from django.core.files.uploadedfile import InMemoryUploadedFile
import hashlib, requests
from django.conf import settings


def send_request_to_client(client_host, submission_path, pno, cname):
    call_back_addr = f'http://{settings.COMPETITIONPLATFORM_SITE_DOMAIN}/submission/create'
    client_addr = client_host + ':' + settings.CLIENT_PORT
    request_url = f'http://{client_addr}?submissionpath={submission_path}&pno={pno}&cname={cname}&callback={call_back_addr}'
    requests.get(request_url, timeout=int(settings.CLIENT_TIMEOUT))


def get_file_md5(file):
    """
    :param file: file-like object
    :return: md5 of file
    """
    md5obj = hashlib.md5()
    md5obj.update(file.read())
    file.seek(0)
    _hash = md5obj.hexdigest()
    return str(_hash).upper()


# zip up a dir
def make_zip(source_dir, output_filename):
    zipf = zipfile.ZipFile(output_filename, 'w')
    pre_len = len(os.path.dirname(source_dir))
    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)  # relative path
            zipf.write(pathfile, arcname)
    zipf.close()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# parse the bundle structure
# check if the bundle structure match the standard, figure out the missing files
# then get the filtered bundle, which will remove the files that not declared in standard
def verify_and_filter_bundle(submission, origin_bundle, client_ip):
    ####################### verify part ##################
    print(client_ip)
    print('[IN validate]', '--' * 50)

    # save origin_bundle to disk (in tmpdir)
    with tempdir() as tmpdir:
        bundle_zip_path = tmpdir + '/bundle.zip'

        with open(bundle_zip_path, 'wb+') as tmpbundle:
            for chunk in origin_bundle.chunks():
                tmpbundle.write(chunk)

        zip_ref = zipfile.ZipFile(bundle_zip_path)

        # extract origin_bundle on disk
        origin_dir = tmpdir + '/origin_bundle'
        os.makedirs(origin_dir)
        zip_ref.extractall(path=origin_dir)

        # get standard structure
        standard_structure = submission.participant.competition.submission_standard
        standard_bundle_name = list(standard_structure.keys())[0]
        standard_files = flatten_dir_structure(standard_structure[standard_bundle_name])
        print('standard: ', standard_files)

        submission_status = '已提交且符合规范'
        status_decided = False
        # get origin_bundle structure: every item in standard should occur in uploaded bundle.
        bundle_structure = get_dir_structure(origin_dir)
        if list(bundle_structure.keys()):
            bundle_name = list(bundle_structure.keys())[0]
            # if submission.participant.pno != bundle_name:   #fixme upload dir name should be pno
            #     return False
            bundle_files = flatten_dir_structure(bundle_structure[bundle_name])
            print('bundle: ', bundle_files)
        else:
            # upload an empty bundle
            bundle_files = []
            submission_status = f'提交失败:选手文件夹{submission.participant.pno}为空'
            status_decided = True
            print('empty bundle uploaded!')

        bundle_files_without_dir = [os.path.split(x)[1] for x in bundle_files]

        missing_files = []
        # start validation
        for file_path in standard_files:
            if file_path in bundle_files:
                # 若一个匹配成功，将当前文件夹下面的其他相同后缀标准文件忽略
                def get_equivalent_file(target, files):
                    equivalent_file = []
                    for f in files:
                        if f != target and target.split('.')[0] == f.split('.')[0]:
                            equivalent_file.append(f)
                    return equivalent_file
                print('@@@@@')
                print(file_path, get_equivalent_file(file_path, standard_files))
                for f in get_equivalent_file(file_path, standard_files):
                    print('!' + f + '!')
                    standard_files.remove(f)
                print(standard_files)
                print('@@@@@')

            if file_path not in bundle_files:
                missing_files.append(os.path.join(submission.participant.pno, file_path))
                if not status_decided:
                    if os.path.split(file_path)[1] in bundle_files_without_dir:
                        # 可能是BJ-01/task1.c 而 标准s是 BJ-01/task1/task1.c
                        submission_status = '已提交:但规定子目录未建'
                        status_decided = True
                    else:
                        submission_status = '已提交:但部分文件未完成'
                        status_decided = True


        submission.status = submission_status
        submission.bundle_structure = bundle_structure
        submission.missing_files = unflatten_dir_structure(missing_files)
        submission.save()
        print('[END validate]', '--' * 50)

        ####################### filter  part ##################
        print('[IN filter]', '--' * 50)

        # create the filtered dir
        filtered_dir = os.path.join(tmpdir, 'filtered_bundle')
        os.makedirs(filtered_dir)

        if list(bundle_structure.keys()):
            bundle_name = list(bundle_structure.keys())[0]
            bundle_files = flatten_dir_structure(bundle_structure[bundle_name])
            print('bundle: ', bundle_files)
            os.makedirs(os.path.join(filtered_dir, bundle_name), exist_ok=True)
            # start filter: move valid stuff in origin_dir to filtered_dir
            for file_path in standard_files:
                if file_path in bundle_files:
                    src = os.path.join(origin_dir, bundle_name, file_path)
                    dest = os.path.join(filtered_dir, bundle_name, file_path)
                    print(src)
                    print(dest)
                    # etc: filtered_bundle/b/c parent is filtered_bundle/b
                    dest_parent = os.path.sep.join(dest.split(os.path.sep)[0:-1])
                    # create filtered_bundle/b recursively
                    os.makedirs(dest_parent, exist_ok=True)

                    # copy file
                    shutil.copy2(src, dest)

            # zip up the filtered bundle in filtered dir
            make_zip(os.path.join(filtered_dir, os.listdir(filtered_dir)[0]),
                     'filtered.zip')  # first and only dir in filtered_dir
        else:
            # todo fixme may be some corner case
            bundle_files = []
            print('empty bundle uploaded!')
            make_zip(filtered_dir, 'filtered.zip')

        print(flatten_dir_structure(get_dir_structure(tmpdir)))

        # assign filtered_bundle to the submission instance
        with open(os.path.join(tmpdir, 'filtered.zip'), 'rb') as f:
            size = os.path.getsize(os.path.join(tmpdir, 'filtered.zip'))
            submission.filtered_bundle = InMemoryUploadedFile(f, origin_bundle.field_name, origin_bundle.name,
                                                              origin_bundle.content_type, size, origin_bundle.charset)
            submission.save()

        print("DONE!")
        print(flatten_dir_structure(get_dir_structure(tmpdir)))
        print('[END filterd]', '--' * 50)

#
# def get_filtered_bundle(submission, origin_bundle):
#     print('[IN filter]', '--' * 50)
#     # save origin_bundle to disk (in tmpdir)
#     with tempdir() as tmpdir:
#         bundle_zip_path = tmpdir + '/bundle.zip'
#
#         with open(bundle_zip_path, 'wb+') as tmpbundle:
#             for chunk in origin_bundle.chunks():
#                 tmpbundle.write(chunk)
#
#         zip_ref = zipfile.ZipFile(bundle_zip_path)
#
#         # extract origin_bundle
#         origin_dir = os.path.join(tmpdir, 'origin_bundle')
#         filtered_dir = os.path.join(tmpdir, 'filtered_bundle')
#         os.makedirs(origin_dir)
#         os.makedirs(filtered_dir)
#         zip_ref.extractall(path=origin_dir)
#
#         # get standard structure
#         standard_structure = submission.participant.competition.submission_standard
#         standard_bundle_name = list(standard_structure.keys())[0]
#         standard_files = flatten_dir_structure(standard_structure[standard_bundle_name])
#         print('standard: ', standard_files)
#
#         # get origin_bundle structure
#         bundle_structure = get_dir_structure(origin_dir)
#         if list(bundle_structure.keys()):
#             bundle_name = list(bundle_structure.keys())[0]
#             bundle_files = flatten_dir_structure(bundle_structure[bundle_name])
#             print('bundle: ', bundle_files)
#             os.makedirs(os.path.join(filtered_dir, bundle_name), exist_ok=True)
#             # start filter: move valid stuff in origin_dir to filtered_dir
#             for file_path in standard_files:
#                 if file_path in bundle_files:
#                     src = os.path.join(origin_dir, bundle_name, file_path)
#                     dest = os.path.join(filtered_dir, bundle_name, file_path)
#                     print(src)
#                     print(dest)
#                     # etc: filtered_bundle/b/c parent is filtered_bundle/b
#                     dest_parent = os.path.sep.join(dest.split(os.path.sep)[0:-1])
#                     # create filtered_bundle/b recursively
#                     os.makedirs(dest_parent, exist_ok=True)
#
#                     # copy file
#                     shutil.copy2(src, dest)
#
#             # zip up the filtered bundle in filtered dir
#             make_zip(os.path.join(filtered_dir, os.listdir(filtered_dir)[0]), 'filtered.zip') # first and only dir in filtered_dir
#         else:
#             # todo fixme may be some corner case
#             bundle_files = []
#             print('empty bundle uploaded!')
#             make_zip(filtered_dir, 'filtered.zip')
#
#         print(flatten_dir_structure(get_dir_structure(tmpdir)))
#
#         # assign filtered_bundle to the submission instance
#         with open(os.path.join(tmpdir, 'filtered.zip'), 'rb') as f:
#             size = os.path.getsize(os.path.join(tmpdir, 'filtered.zip'))
#             submission.filtered_bundle = InMemoryUploadedFile(f, origin_bundle.field_name, origin_bundle.name,
#                                                               origin_bundle.content_type, size, origin_bundle.charset)
#             submission.save()
#
#         print("DONE!")
#         print(flatten_dir_structure(get_dir_structure(tmpdir)))
#         print('[END filterd]', '--' * 50)
#         return True
#
#
# # parse the bundle structure
# # check if the bundle structure match the standard, figure out the missing files
# def verify_bundle(submission, origin_bundle):
#     print('[IN validate]', '--' * 50)
#     # save origin_bundle to disk (in tmpdir)
#     with tempdir() as tmpdir:
#         bundle_zip_path = tmpdir + '/bundle.zip'
#
#         with open(bundle_zip_path, 'wb+') as tmpbundle:
#             for chunk in origin_bundle.chunks():
#                 tmpbundle.write(chunk)
#
#         zip_ref = zipfile.ZipFile(bundle_zip_path)
#
#         # extract origin_bundle on disk
#         bundle_path = tmpdir + '/bundle'
#         os.makedirs(bundle_path)
#         zip_ref.extractall(path=bundle_path)
#
#         # get standard structure
#         standard_structure = submission.participant.competition.submission_standard
#         standard_bundle_name = list(standard_structure.keys())[0]
#         standard_files = flatten_dir_structure(standard_structure[standard_bundle_name])
#         print('standard: ', standard_files)
#
#         # get origin_bundle structure: every item in standard should occur in uploaded bundle.
#         bundle_structure = get_dir_structure(bundle_path)
#         if list(bundle_structure.keys()):
#             bundle_name = list(bundle_structure.keys())[0]
#             # if submission.participant.pno != bundle_name:   #fixme upload dir name should be pno
#             #     return False
#             bundle_files = flatten_dir_structure(bundle_structure[bundle_name])
#             print('bundle: ', bundle_files)
#         else:
#             # upload an empty bundle
#             bundle_files = []
#             print('empty bundle uploaded!')
#
#         missing_files = []
#         status = '已提交且符合规范'
#         # start validation
#         for file_path in standard_files:
#             if file_path not in bundle_files:
#                 status = '已提交但部分文件缺失'
#                 missing_files.append(file_path)
#
#         submission.status = status
#         submission.bundle_structure = bundle_structure
#         submission.missing_files = unflatten_dir_structure(missing_files)
#         submission.save()
#         print('[END validate]', '--' * 50)
