import time

from pyzbar.pyzbar import decode
from PIL import Image
import requests
import tempfile
import os


def decode_from_url(url):
    r = requests.get(url, allow_redirects=True)
    filename = __get_temp_filename()
    open(filename, 'wb').write(r.content)
    result = __decode_from_file(filename)
    os.remove(filename)
    return result


def __decode_from_file(filename):
    try:
        d = decode(Image.open(filename))
        if d and len(d) > 0:
            d0 = d[0]
            return d0.data.decode('utf-8')
    except Exception as e:
        print(e)
        pass
    return ''


def __get_temp_filename():
    temp_dir = tempfile._get_default_tempdir()
    temp_name = next(tempfile._get_candidate_names())
    return os.path.join(temp_dir, temp_name)
