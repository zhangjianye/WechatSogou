import base64
import json
import requests

user_name = 'weichat'
password = '142857'
typeid = 3


def image_identify_from_file(img_file):
    try:
        with open(img_file, 'rb') as f:
            data = f.read()
    except:
        return ""
    return image_identify(data)


def image_identify(img_data):
    base64_data = base64.b64encode(img_data).decode('utf-8')
    return __get_result(base64_data)


def __get_result(img_data_str):
    data = {"username": user_name, "password": password, "typeid": typeid, "image": img_data_str}
    try:
        result = json.loads(requests.post("http://api.ttshitu.com/predict", json=data).text)
        print(result)
        if result['success']:
            return result["data"]["result"]
        else:
            return ""
    except:
        return ""


def test_image_identify():
    uname = 'weichat'
    pwd = '142857'
    filename = '/Users/zhangjianye/Downloads/ymksvb.jpeg'
    typeid = 3
    print(image_identify_from_file(filename))
