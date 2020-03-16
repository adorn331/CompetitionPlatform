from apps.detector.tasks import calculate_submission_similarity
import subprocess, os


def inspect_plagiarism(competition, submission):
    for p in competition.participants.all():
        previous_submission = p.uploaded_submission.first()
        if previous_submission:
            calculate_submission_similarity.apply_async((competition.id, submission.id, previous_submission.id))


def calculate_file_similarity(src_path, dest_path):
    print("!!!")
    print(src_path, dest_path)

    fdir, fname = os.path.split(src_path)
    # todo in windows?
    res = subprocess.run(["sim_c", "-p", src_path, dest_path], capture_output=True)

    if not res.stderr:
        print(str(res.stdout))
    else:
        print(str(res.stderr))

    print("!!!")
