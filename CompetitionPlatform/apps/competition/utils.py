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


def flatten_dir_structure(dictionary):
    res = []

    def reach_bottom(v):
        return len(v.keys()) == 0 # substree is {}

    def helper(dictionary, prefix=''):
        for k, v in dictionary.items():
            if reach_bottom(v):
                res.append(os.path.join(prefix, k))
            else:
                helper(v, os.path.join(prefix, k))

    helper(dictionary)

    return res


def unflatten_dir_structure(flatten_list):
    resultDict = dict()
    for i in flatten_list:
        parts = i.split(os.path.sep)
        d = resultDict
        for part in parts[:-1]:
            if part not in d:
                d[part] = dict()
            d = d[part]
        d[parts[-1]] = {}
    return resultDict


def get_dir_structure(dir):
    result = {}     # todo bundle generate from the last path from dir?
    for item in os.listdir(dir):
        if item == '__MACOSX' or item == '.DS_Store':
            continue
        item_path = os.path.join(dir, item)
        if os.path.isdir(item_path):
            result[item] = get_dir_structure(item_path)
        else:
            result[item] = {}
    return result


def parse_participants(mem_csv_file, competition):
    # parse participants
    with tempdir() as tmpdir:
        # save memory file to disk
        with open(tmpdir + 'tmp.csv', 'wb+') as tmpcsv:
            for chunk in mem_csv_file.chunks():
                tmpcsv.write(chunk)
        # parse csv file to real participants
        with open(tmpdir + 'tmp.csv', 'r', encoding='utf-8-sig') as tmpcsv:
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

                if len(line) >= 7:
                    # parse the position
                    position = line[6]
                    participant.position = position

                participant.competition = competition
                participant.save()


def parse_hosts(mem_csv_file, competition):
    # parse participants
    with tempdir() as tmpdir:
        # save memory file to disk
        with open(tmpdir + 'tmp.csv', 'wb+') as tmpcsv:
            for chunk in mem_csv_file.chunks():
                tmpcsv.write(chunk)
        # parse csv file to real participants
        with open(tmpdir + 'tmp.csv', 'r', encoding='utf-8-sig') as tmpcsv:
            reader = csv.reader(tmpcsv)
            for line in reader:
                position = line[0]
                host = line[1]
                print(position, host)
                participant = competition.participants.filter(position=position).first()
                if participant:
                    participant.host = host
                    participant.save()



def parse_standard_from_bundle(mem_bundle_file):
    # save mem_bundle_file on disk
    with tempdir() as tmpdir:
        bundle_zip_path = tmpdir + '/bundle.zip'

        with open(bundle_zip_path, 'wb+') as tmpbundle:
            for chunk in mem_bundle_file.chunks():
                tmpbundle.write(chunk)

        # extract them on disk
        zip_ref = zipfile.ZipFile(bundle_zip_path)
        bundle_path = tmpdir + '/bundle'
        zip_ref.extractall(path=bundle_path)

        print(get_dir_structure(bundle_path))
        return get_dir_structure(bundle_path)
