import hashlib
import os


def hashsum(bytes):
    m = hashlib.sha256()
    m.update(bytes)
    return m.hexdigest()


def get_filetype(path):
    _, ext = os.path.splitext(path)
    return ext[1:]
