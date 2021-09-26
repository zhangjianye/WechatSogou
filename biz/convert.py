import time
import queue
import requests
import json
import threading
from common.singleton import Singleton
from .datatype import Article


class ConvertException(Exception):
    # raise when something wrong in process of converting task
    pass


class Converter(metaclass=Singleton):
    def __init__(self, keys=[]):
        self._keys = keys
        self._convert_url = 'https://api.newrank.cn/api/async/task/sogou/towxurl'
        self._result_url = 'https://api.newrank.cn/api/task/result'
        self._index = 0
        self._queue = queue.Queue()
        self._failed_queue = queue.Queue()
        self._finished = False

    def convert(self, articles: [Article], finished_method):
        def create_task(a: Article):
            if self._index >= len(self._keys):
                raise ConvertException('no more valid key')
            key = self._keys[self._index]
            data = {
                'url': a.temp_url
            }
            header = {
                'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
                'Key': key
            }
            response = requests.post(self._convert_url, data=data, headers=header)
            result = json.loads(response.text)
            if result['code'] != 0:
                raise ConvertException('post failed, code={}'.format(result['code']))
            task_id = result['data']['taskId']
            self._queue.put((a, key, task_id))
            print('task created, index={} temp-url={}, task-id={}'.format(a.index, a.temp_url, task_id))

        def query_result():
            while not self._finished or not self._queue.empty():
                item = self._queue.get()
                a = item[0]
                key = item[1]
                task_id = item[2]
                self._queue.task_done()
                data = {
                    'taskId': task_id
                }
                header = {
                    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
                    'Key': key
                }
                url = ''
                succeed = False
                slept = False
                while True:
                    response = requests.post(self._result_url, data=data, headers=header)
                    result = json.loads(response.text)
                    code = result['code']
                    if code == 0:
                        tasks = result['task']
                        if len(tasks) > 0:
                            url = tasks[0]['url']
                            succeed = True
                            break
                        else:
                            break
                    elif code in (1104, 1105, 1108, 1109):
                        self._index += 1
                        break
                    elif code in (2200, 2201, 2202):
                        time.sleep(1)
                        slept = True
                    else:
                        print('task failed, code:{}'.format(code))
                        break
                if succeed:
                    if len(url) > 0:
                        print('convert succeed, index={}, url={}'.format(a.index, url))
                        a.url = url
                        finished_method(a)
                else:
                    print('add to retry queue, index={}'.format(a.index))
                    self._failed_queue.put(a)
                if not slept:
                    time.sleep(1)

        thread = threading.Thread(target=query_result, daemon=True)
        thread.start()
        for a in articles:
            create_task(a)
            time.sleep(1)
        while not self._failed_queue.empty():
            a = self._failed_queue.get()
            create_task(a)
            time.sleep(1)
        self._queue.join()
        self._finished = True
        thread.join()
        # while not done:
        #     time.sleep()

