# for utils
import contextlib
import os
import shutil
import tempfile


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
