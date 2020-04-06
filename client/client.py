from flask import Flask
from flask import request
import zipfile, os, time,  hashlib, logging, shutil
from logging import FileHandler

app = Flask(__name__)

@app.route('/')
def listen_from_server():
    call_back_addr = request.args.get("callback")
    submission_path = request.args.get("submissionpath")
    pno = request.args.get("pno")
    cname = request.args.get("cname")
    app.logger.info(f'pno:{pno}')
    app.logger.info(f'cname:{cname}')
    app.logger.info(f'submission_path:{submission_path}')
    app.logger.info(f'callback_addr:{call_back_addr}')
    upload_submission(call_back_addr, submission_path, pno, cname)
    return '200'

def upload_submission(call_back_addr, submission_path, pno, cname):
    # zip up the submission
    submission_bundle_path = f'{pno}.zip'
    copied_submission_path = f'C:\{pno}' # todo change C to a tmp dir, can transplant between diff platform
    if os.path.exists(copied_submission_path):
        shutil.rmtree(copied_submission_path)
    shutil.copytree(submission_path,copied_submission_path)
    shutil.rmtree(copied_submission_path)
    _make_zip(copied_submission_path, submission_bundle_path)

    # cal md5
    with open(submission_bundle_path, 'rb') as bundle:
        md5 = _get_file_md5(bundle)

    # post to call back
    import requests
    files = {
        "file": open(submission_bundle_path, "rb")
    }

    call_back_url = call_back_addr + f'?pno={pno}&cname={cname}&md5={md5}'
    requests.post(call_back_url, files=files)
  

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
    app.debug = True
    handler = logging.FileHandler('client.log')
    app.logger.addHandler(handler)
    app.run('0.0.0.0')