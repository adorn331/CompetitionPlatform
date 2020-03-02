from apps.competition.utils import tempdir, get_dir_structure, flatten_dir_structure, unflatten_dir_structure
import zipfile, os, shutil
from django.core.files.uploadedfile import InMemoryUploadedFile
import hashlib


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


def get_filtered_bundle(submission, origin_bundle):
    print('[IN filter]', '--' * 50)
    # save origin_bundle to disk (in tmpdir)
    with tempdir() as tmpdir:
        bundle_zip_path = tmpdir + '/bundle.zip'

        with open(bundle_zip_path, 'wb+') as tmpbundle:
            for chunk in origin_bundle.chunks():
                tmpbundle.write(chunk)

        zip_ref = zipfile.ZipFile(bundle_zip_path)

        # extract origin_bundle
        origin_dir = os.path.join(tmpdir, 'origin_bundle')
        filtered_dir = os.path.join(tmpdir, 'filtered_bundle')
        zip_ref.extractall(path=origin_dir)

        # get standard structure
        standard_structure = submission.participant.competition.submission_standard
        standard_bundle_name = list(standard_structure.keys())[0]
        standard_files = flatten_dir_structure(standard_structure[standard_bundle_name])
        print('standard: ', standard_files)

        # get origin_bundle structure
        bundle_structure = get_dir_structure(origin_dir)
        bundle_name = list(bundle_structure.keys())[0]
        bundle_files = flatten_dir_structure(bundle_structure[bundle_name])
        print('bundle: ', bundle_files)

        print(flatten_dir_structure(get_dir_structure(tmpdir)))
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
        make_zip(os.listdir(filtered_dir)[0], 'filtered.zip')

        # assign filtered_bundle to the submission instance
        with open(os.path.join(tmpdir, 'filtered.zip'), 'rb') as f:
            size = os.path.getsize(os.path.join(tmpdir, 'filtered.zip'))
            submission.filtered_bundle = InMemoryUploadedFile(f, origin_bundle.field_name, origin_bundle.name,
                                                              origin_bundle.content_type, size, origin_bundle.charset)
            submission.save()

        print("DONE!")
        print(flatten_dir_structure(get_dir_structure(tmpdir)))
        print('[END filterd]', '--' * 50)
        return True


# parse the bundle structure
# check if the bundle structure match the standard, figure out the missing files
def verify_bundle(submission, origin_bundle):
    print('[IN validate]', '--' * 50)
    # save origin_bundle to disk (in tmpdir)
    with tempdir() as tmpdir:
        bundle_zip_path = tmpdir + '/bundle.zip'

        with open(bundle_zip_path, 'wb+') as tmpbundle:
            for chunk in origin_bundle.chunks():
                tmpbundle.write(chunk)

        zip_ref = zipfile.ZipFile(bundle_zip_path)

        # extract origin_bundle on disk
        bundle_path = tmpdir + '/bundle'
        zip_ref.extractall(path=bundle_path)

        # get standard structure
        standard_structure = submission.participant.competition.submission_standard
        standard_bundle_name = list(standard_structure.keys())[0]
        standard_files = flatten_dir_structure(standard_structure[standard_bundle_name])
        print('standard: ', standard_files)

        # get origin_bundle structure: every item in standard should occur in uploaded bundle.
        bundle_structure = get_dir_structure(bundle_path)
        bundle_name = list(bundle_structure.keys())[0]
        # if submission.participant.pno != bundle_name:   # upload dir name should be pno
        #     return False
        bundle_files = flatten_dir_structure(bundle_structure[bundle_name])
        print('bundle: ', bundle_files)

        missing_files = []
        valid = True
        # start validation
        for file_path in standard_files:
            if file_path not in bundle_files:
                valid = False
                missing_files.append(file_path)

        submission.bundle_structure = bundle_structure
        submission.missing_files = unflatten_dir_structure(missing_files)
        submission.save()
        print('[END validate]', '--' * 50)
        return valid
