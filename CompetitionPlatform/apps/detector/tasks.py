from CompetitionPlatform.celery import app
from apps.submission.models import Submission
from apps.competition.models import Competition
from apps.competition.utils import tempdir, get_dir_structure, flatten_dir_structure, unflatten_dir_structure
import os, zipfile
from apps.detector.models import Similarity


@app.task(queue='site-worker', soft_time_limit=60 * 60 * 24)
def hello_site():
    print("hello! from site-worker")


@app.task(queue='site-worker', soft_time_limit=60 * 5)
def calculate_submission_similarity(competition_id, src_sub_id, dest_sub_id):
    print('$' * 50)
    print(competition_id, src_sub_id, dest_sub_id)
    competition = Competition.objects.get(pk=competition_id)
    src_sub = Submission.objects.get(pk=src_sub_id)
    dest_sub = Submission.objects.get(pk=dest_sub_id)

    with tempdir() as tmpdir:
        # extract src_bundle
        src_zip_ref = zipfile.ZipFile(src_sub.bundle.path) # todo use filetered_bundle?
        src_dir = os.path.join(tmpdir, 'src_bundle')
        src_zip_ref.extractall(path=src_dir)
        # get src_bundle structure & files
        src_bundle_structure = get_dir_structure(src_dir)
        if list(src_bundle_structure.keys()):
            src_bundle_name = list(src_bundle_structure.keys())[0]
            src_bundle_files = flatten_dir_structure(src_bundle_structure[src_bundle_name])
        else:
            src_bundle_files = []
        print('src bundle: ', src_bundle_files)


        # extract dest_bundle
        dest_zip_ref = zipfile.ZipFile(dest_sub.bundle.path) # todo use filetered_bundle?
        dest_dir = os.path.join(tmpdir, 'dest_bundle')
        dest_zip_ref.extractall(path=dest_dir)
        # get dest_bundle structure & files
        dest_bundle_structure = get_dir_structure(dest_dir)
        if list(dest_bundle_structure.keys()):
            dest_bundle_name = list(dest_bundle_structure.keys())[0]
            dest_bundle_files = flatten_dir_structure(dest_bundle_structure[dest_bundle_name])
        else:
            dest_bundle_files = []
        print('dest bundle: ', dest_bundle_files)

        # start to compare each file's similarity
        for src_fname in src_bundle_files:
            if src_fname in dest_bundle_files:
                # todo only check the legal suffix of file(don't care about other stuff)
                src_path = os.path.join(src_dir, src_bundle_name, src_fname)
                dest_path = os.path.join(dest_dir, dest_bundle_name, src_fname)

                from apps.detector.utils import calculate_file_similarity
                sim_percentage = calculate_file_similarity(src_path, dest_path)

                similarity_record = Similarity()
                similarity_record.percentage = sim_percentage
                similarity_record.src_submission = src_sub
                similarity_record.dest_submission = dest_sub
                similarity_record.src_file = os.path.split(src_path)[-1]
                similarity_record.dest_file = os.path.split(dest_path)[-1]
                similarity_record.competition = competition
                similarity_record.save()

    print('$' * 50)
