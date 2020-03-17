from apps.detector.tasks import calculate_submission_similarity
import subprocess, os, re


def inspect_plagiarism(competition, submission):
    for p in competition.participants.all():
        previous_submission = p.uploaded_submission.first()
        if previous_submission:
            calculate_submission_similarity.apply_async((competition.id, submission.id, previous_submission.id))


def calculate_file_similarity(src_path, dest_path):
    print("!!!")
    print(src_path, dest_path)

    fdir, fname = os.path.split(src_path)
    suffix = str(fname.split('.')[-1]).lower()
    suffix_sim_mapping = {
        'c': 'sim_c',
        'cpp': 'sim_c++',
        'java': 'sim_java',
        'pas': 'sim_pasc',
        'lisp': 'sim_lisp',
        'lsp': 'sim_lisp',
    }

    res = subprocess.run([suffix_sim_mapping.get(suffix, 'sim_text'), "-p", src_path, dest_path], capture_output=True)

    if not res.stderr:
        print(str(res.stdout))

        match = re.search('(\d+) %', str(res.stdout))
        sim_percentage = match.group(1) if match else 0
        print('@@@@@@@@@@')
        print(sim_percentage)
        print('@@@@@@@@@@')
        return sim_percentage

    else:
        print(str(res.stderr))

    print("!!!")
