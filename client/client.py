from flask import Flask
from flask import request
import zipfile, os, time,  hashlib

app = Flask(__name__)

@app.route('/')
def listen_from_server():
    call_back_addr = request.args.get("callback")
    submission_path = request.args.get("submissionpath")
    pno = request.args.get("pno")
    cname = request.args.get("cname")
    print(call_back_addr)
    print(submission_path)
    upload_submission(call_back_addr, submission_path, pno, cname)
    return '200'

def upload_submission(call_back_addr, submission_path, pno, cname):
    # zip up the submission
    submission_bundle_path = 'submission.zip'
    _make_zip(submission_path, submission_bundle_path)

    # cal md5
    with open(submission_bundle_path, 'rb') as bundle:
        md5 = _get_file_md5(bundle)
    print(md5)

    # post to call back
    import requests
    files = {
        "file": open(submission_bundle_path, "rb")
    }

    call_back_url = call_back_addr + f'?pno={pno}&cname={cname}&md5={md5}'
    requests.post(call_back_url, files=files)

    # clean the zip
    os.remove(submission_bundle_path)
  

# zip up a dir
def _make_zip(source_dir, output_path):
    zipf = zipfile.ZipFile(output_path, 'w')
    pre_len = len(os.path.dirname(source_dir))
    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)  # relative path
            zipf.write(pathfile, arcname)
    zipf.close()

def _get_file_md5(file):
    """
    :param file: file-like object
    :return: md5 of file
    """
    md5obj = hashlib.md5()
    md5obj.update(file.read())
    file.seek(0)
    _hash = md5obj.hexdigest()
    return str(_hash).upper()

if __name__ == '__main__':
    app.run('0.0.0.0')