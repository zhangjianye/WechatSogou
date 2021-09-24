import pymongo
import pymongo.errors
from common.singleton import Singleton
from biz.datatype import Article, Account


class Storage(metaclass=Singleton):
    def __init__(self, connection_string=''):
        mongo_client = pymongo.MongoClient(connection_string)
        try:
            _ = mongo_client.server_info()
            mongo_db = mongo_client['wechat']
            self._db_articles = mongo_db['articles']
            # self._db_articles.insert_one({'test': 'test'})
            self._db_objects = mongo_db['objects']
            # self._db_objects.insert_one({'test': 'test'})
            self._connected = True
        except pymongo.errors.PyMongoError as err:
            print("connect to mongodb {} failed, err: {}".format(connection_string, err))
            self._db_articles = None
            self._db_objects = None
            self._connected = False

    # @classmethod
    # def instance(cls):
    #     return cls._instance

    def connected(self) -> bool:
        return self._connected

    def __load_object(self, object_name):
        return self._db_objects.find_one({'name': object_name})

    def __load_or_create_object(self, object_name):
        query = {'name': object_name}
        object = self._db_objects.find_one(query)
        last_index = 0
        if object is None:
            object_id = self._db_objects.insert_one({'name': object_name, 'last_index': 0}).inserted_id
        else:
            object_id = object['_id']
            last_index = object['last_index']
        return object_id, last_index

    def __modify_object_last_index(self, object_id, last_index):
        query = {'_id': object_id}
        update = {'$set': {'last_index': last_index}}
        self._db_objects.update_one(query, update)

    def load_article_set(self, object_name):
        obj = self.__load_object(object_name)
        result = set()
        if obj is not None:
            articles = self.__load_articles_for_set(obj['_id'])
            for a in articles:
                combination = (a['title'], a['wechat_name'], a['time'])
                result.add(combination)
        return result

    def save_articles(self, object_name, articles: [Article]):
        object_id, index = self.__load_or_create_object(object_name)
        records = []
        for a in articles:
            index += 1
            record = {
                'object_id': object_id,
                'index': index,
                'title': a.title,
                'temp_url': a.url,
                'url': '',
                'time': a.time,
                'wechat_name': a.wechat_name,
                'profile_url': a.profile_url,
                'isv': a.isv,
                'gzh': {
                    'name': a.gzh.name,
                    'avatar': a.gzh.avatar,
                    'principal': a.gzh.principal,
                    'wechat_id': a.gzh.wechat_id,
                    'desc': a.gzh.desc,
                    'qr_code': a.gzh.qr_code
                },
                'imgs': a.imgs
            }
            records.append(record)
        self._db_articles.insert_many(records)
        self.__modify_object_last_index(object_id, index)

    def load_articles(self, object_name):
        pass

    def __load_articles_for_set(self, object_id):
        query = {'object_id': object_id}
        columns = {'_id': 0, 'title': 1, 'wechat_name': 1, 'time': 1}
        return self._db_articles.find(query, columns)
