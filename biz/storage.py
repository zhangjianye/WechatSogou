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

    def load_article_set(self, object_name):
        obj = self.__load_object(object_name)
        result = set()
        if obj is not None:
            articles = self.__load_articles_for_set(obj['_id'])
            for a in articles:
                combination = (a['title'], a['wechat_name'], a['time'])
                result.add(combination)
        return result

    def save_articles(self, object_name, keyword, articles: [Article]):
        object_id, index = self.__load_or_create_object(object_name)
        records = []
        for a in articles:
            index += 1
            record = {
                'object_id': object_id,
                'index': index,
                'keyword': keyword,
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

    def load_articles(self, object_name, begin_index=0, end_index=0, limit=0, empty_url=False):
        object_id = self.__get_object_id(object_name)
        query = {
            'object_id': object_id,
        }
        if begin_index > 0 or end_index > 0:
            query['index'] = {}
            if begin_index > 0:
                query['index']['$gte'] = begin_index
            if end_index > 0:
                query['index']['$lte'] = end_index
        if empty_url:
            query['url'] = ''
        if limit > 0:
            result = self._db_articles.find(query).limit(limit)
        else:
            result = self._db_articles.find(query)
        return (self.__dict_to_article(d) for d in result)

    def update_article_url(self, article: Article):
        query = {'_id': article.id}
        update = {'$set': {'url': article.url}}
        self._db_articles.update_one(query, update)

    def __load_object(self, object_name):
        return self._db_objects.find_one({'name': object_name})

    def __get_object_id(self, object_name):
        query = {'name': object_name}
        object = self._db_objects.find_one(query)
        return object['_id']

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

    def __load_articles_for_set(self, object_id):
        query = {'object_id': object_id}
        columns = {'_id': 0, 'title': 1, 'wechat_name': 1, 'time': 1}
        return self._db_articles.find(query, columns)

    @staticmethod
    def __dict_to_article(d) -> Article:
        account = Account()
        gzh = d['gzh']
        account.name = gzh['name']
        account.avatar = gzh['avatar']
        account.principal = gzh['principal']
        account.wechat_id = gzh['wechat_id']
        account.desc = gzh['desc']
        account.qr_code = gzh['qr_code']
        article = Article(id=d['_id'],
                          index=d['index'],
                          title=d['title'],
                          url=d['url'],
                          temp_url=d['temp_url'],
                          time=d['time'],
                          wechat_name=d['wechat_name'],
                          profile_url=d['profile_url'],
                          isv=d['isv'],
                          gzh=account)
        article.imgs = d['imgs']
        return article
