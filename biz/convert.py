import time

import requests
import json
from common.singleton import Singleton


class ConvertException(Exception):
    # raise when something wrong in process of converting task
    pass


class Converter(metaclass=Singleton):
    def __init__(self, keys=[]):
        self._keys = keys
        self._convert_url = 'https://api.newrank.cn/api/async/task/sogou/towxurl'
        self._result_url = 'https://api.newrank.cn/api/task/result'
        self._index = 0

    def convert(self, temp_url):
        while True:
            if self._index >= len(self._keys):
                raise ConvertException('no more valid key')
            key = self._keys[self._index]
            data = {
                'url': temp_url
            }
            header = {
                'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
                'Key': key
            }
            response = requests.post(self._convert_url, data=data, headers=header)
            result = json.loads(response.text)
            if result['code'] != 0:
                raise ConvertException('post failed')
            task_id = result['data']['taskId']
            while True:
                data = {
                    'taskId': task_id
                }
                response = requests.post(self._result_url, data=data, headers=header)
                result = json.loads(response.text)
                code = result['code']
                if code == 0:
                    tasks = result['task']
                    if len(tasks) > 0:
                        return tasks[0]['url']
                    else:
                        return ''
                elif code in (1104, 1105, 1108, 1109):
                    self._index += 1
                    break
                elif code in (2200, 2201, 2202):
                    time.sleep(0.5)
                else:
                    raise ConvertException('task failed, code:{}'.format(code))
