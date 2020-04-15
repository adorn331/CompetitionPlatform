from apps.detector.tasks import calculate_submission_similarity
from apps.competition.models import Participant
from apps.submission.models import Submission
import subprocess, os, re, json
from apps.competition.utils import turn_0_1_to_num_matrix


def inspect_plagiarism(competition, submission):
    # from apps.competition.utils import parse_position
    #
    # def is_around(sub1, sub2):
    #     if sub1.id == sub2.id: # don't compare with it self
    #         return False
    #
    #     pos1 = sub1.participant.position if sub1.participant.position else '1-1'
    #     x1, y1 = parse_position(pos1)
    #     pos2 = sub2.participant.position if sub2.participant.position else '1-1'
    #     x2, y2 = parse_position(pos2)
    #
    #     if abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1:
    #         return True
    #     else:
    #         return False
    #
    # for p in competition.participants.all():
    #     previous_submission = p.uploaded_submission.first()
    #     if previous_submission:
    #         if is_around(previous_submission,submission): # only compare with the around
    #             calculate_submission_similarity.apply_async((competition.id, submission.id, previous_submission.id))
    #
    print('$' * 60)
    def get_neighbors_submission(layout, x, y):
        ret = []
        delta_x = (0, 0, 1, 1, -1, -1, 1, -1)
        delta_y = (1, -1, 1, -1, 1, -1, 0, 0)
        m = len(layout)
        n = len(layout[0])
        for delta_index in range(8):
            nx = x + delta_x[delta_index]
            ny = y + delta_y[delta_index]
            if 0 <= nx < m and 0 <= ny < n and layout[nx][ny] != 0:
                p = Participant.objects.filter(competition=competition, position=layout[nx][ny]).first()
                if p and p.uploaded_submission.count() > 0:
                    ret.append(p.uploaded_submission.first())
        return ret

    position = submission.participant.position
    layout_str = competition.room_layout.layout_matrix
    layout = json.loads(layout_str)
    turn_0_1_to_num_matrix(layout)
    for i in range(len(layout)):
        for j in range(len(layout[0])):
            if layout[i][j] == int(position):
                for sub in get_neighbors_submission(layout, i, j):

                    print(submission.participant)
                    print(sub.participant)

                    calculate_submission_similarity.apply_async((competition.id, submission.id, sub.id))
    print('$' * 60)


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
