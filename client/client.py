from flask import Flask
from flask import request
import zipfile, os, time,  hashlib, logging, shutil, tempfile, contextlib, requests
import _thread
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
    _thread.start_new_thread(upload_submission,(call_back_addr, submission_path, pno, cname))
    #upload_submission(call_back_addr, submission_path, pno, cname)
    return '200'


def upload_submission(call_back_addr, submission_path, pno, cname):
    with _tempdir() as tmpdir:
        target_path = os.path.join(submission_path, pno)
        app.logger.info(target_path)
        if os.path.exists(target_path):
            # zip up the submission
            copied_submission_path = os.path.join(tmpdir, pno)
            shutil.copytree(target_path,copied_submission_path)
            submission_bundle_path = os.path.join(tmpdir, f'{pno}.zip')
            _make_zip(copied_submission_path, submission_bundle_path)

            # cal md5
            with open(submission_bundle_path, 'rb') as bundle:
                md5 = _get_file_md5(bundle)

            # post to call back
            files = {
                "file": open(submission_bundle_path, "rb")
            }

            call_back_url = call_back_addr + f'?pno={pno}&cname={cname}&md5={md5}'
            requests.post(call_back_url, files=files)
        else:
            call_back_url = call_back_addr + f'?pno={pno}&cname={cname}'
            requests.post(call_back_url)
  

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
def _tempdir():
    dirpath = tempfile.mkdtemp()

    def cleanup():
        shutil.rmtree(dirpath)

    with _cd(dirpath, cleanup):
        yield dirpath


if __name__ == '__main__':
    app.debug = True
    handler = logging.FileHandler('client.log')
    app.logger.addHandler(handler)
    app.run('0.0.0.0')