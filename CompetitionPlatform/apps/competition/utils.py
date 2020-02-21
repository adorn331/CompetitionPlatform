# for utils
import contextlib
import os
import shutil
import tempfile
from apps.competition.models import Competition, Participant
import csv, zipfile


# these two function are used to support tmp dir
@contextlib.contextmanager
def _cd(newdir, cleanup):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)
        cleanup()


@contextlib.contextmanager
def tempdir():
    dirpath = tempfile.mkdtemp()

    def cleanup():
        shutil.rmtree(dirpath)

    with _cd(dirpath, cleanup):
        yield dirpath


def get_dir_structure(dir):
    result = {}
    for item in os.listdir(dir):
        item_path = os.path.join(dir, item)
        if os.path.isdir(item_path):
            result[item] = get_dir_structure(item_path)
        else:
            result[item] = item
    return result

# def get_dir_structure(dir):
#     result = []
#     for item in os.listdir(dir):
#         item_path = os.path.join(dir, item)
#         if os.path.isdir(item_path):
#             result.append({item:get_dir_structure(item_path)})
#         else:
#             result.append(item)
#     return result


def parse_participants(mem_csv_file, competition):
    # parse participants
    with tempdir() as tmpdir:
        # save memory file to disk
        with open(tmpdir + 'tmp.csv', 'wb+') as tmpcsv:
            for chunk in mem_csv_file.chunks():
                tmpcsv.write(chunk)
        # parse csv file to real participants
        with open(tmpdir + 'tmp.csv', 'r') as tmpcsv:
            reader = csv.reader(tmpcsv)
            for line in reader:
                print(line)
                participant = Participant()
                participant.pno = line[0]
                participant.province = line[1]
                participant.name = line[2]
                participant.id_num = line[3]
                participant.school = line[4]
                participant.grade = line[5]
                participant.save()
                competition.participants.add(participant)


def parse_standard_from_bundle(mem_bundle_file):
    with tempdir() as tmpdir:
        bundle_zip_path = tmpdir + '/upload.zip'

        with open(bundle_zip_path, 'wb+') as tmpbundle:
            for chunk in mem_bundle_file.chunks():
                tmpbundle.write(chunk)

        zip_ref = zipfile.ZipFile(bundle_zip_path)

        bundle_path = tmpdir + '/bundle'
        zip_ref.extractall(path=bundle_path)

        return get_dir_structure(bundle_path)