import pymongo
import pymongo.errors
from common.singleton import Singleton
from biz.datatype import Article, Account
from datetime import datetime


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
            self._db_accounts = mongo_db['accounts']
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

    def save_articles(self, object_name, keyword, articles: [Article], batch, last_page, finished):
        object_id, index = self.__load_or_create_object(object_name)
        records = []
        for a in articles:
            index += 1
            record = {
                'object_id': object_id,
                'index': index,
                'keyword': keyword,
                'title': a.title,
                'temp_url': a.temp_url,
                'url': a.url,
                'time': a.time,
                'wechat_name': a.wechat_name,
                'profile_url': a.profile_url,
                'isv': a.isv,
                'gzh_id': a.gzh_id,
                'imgs': a.imgs,
                'batch': batch,
            }
            records.append(record)
        self._db_articles.insert_many(records)
        self.__update_object_info(object_id, index, batch, keyword, last_page, finished)

    def load_articles(self, object_name, begin_index=0, end_index=0, limit=0, empty_url=False, batch='',
                      expand_account=False, verified_only=False):
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
        if len(batch) > 0:
            query['batch'] = batch
        if verified_only:
            query['isv'] = 1
        if limit > 0:
            result = self._db_articles.find(query).limit(limit)
        else:
            result = self._db_articles.find(query)
        articles = [self.__dict_to_article(d) for d in result]
        if expand_account:
            self.expand_account_of_articles(articles)
        return articles

    def expand_account_of_articles(self, articles):
        cache = {}
        for a in articles:
            if a.gzh_id in cache:
                a.gzh = cache[a.gzh_id]
            else:
                gzh = self.load_account_by_id(a.gzh_id)
                a.gzh = gzh
                cache[a.gzh_id] = gzh

    def update_article_url(self, article: Article):
        query = {'_id': article.id}
        update = {'$set': {'url': article.url}}
        self._db_articles.update_one(query, update)

    # def update_article_gzh(self, article: Article):
    #     query = {'_id': article.id}
    #     update = {'$set': {
    #         'gzh.wechat_id': article.gzh.wechat_id,
    #         'gzh.name': article.gzh.name,
    #         'gzh.avatar': article.gzh.avatar,
    #         'gzh.principal': article.gzh.principal,
    #         'gzh.desc': article.gzh.desc
    #     }}
    #     self._db_articles.update_one(query, update)

    def test_account(self, name):
        record = self._db_accounts.find_one({'name': name})
        return record['_id'] if record is not None else None

    def load_account_by_name(self, name):
        record = self._db_accounts.find_one({'name': name})
        if record is None:
            return None
        else:
            return self.__dict_to_account(record)

    def load_account_by_id(self, id):
        record = self._db_accounts.find_one({'_id': id})
        if record is None:
            return None
        else:
            return self.__dict_to_account(record)

    def save_account(self, account: Account):
        record = self.__account_to_dict(account)
        if account.id is None:
            account.id = self._db_accounts.insert_one(record).inserted_id
        else:
            query = {'_id': account.id}
            self._db_accounts.update_one(query, {'$set': record})

    def load_object_info(self, object_name, batch, verified_only):
        obj = self.__load_object(object_name)
        if obj is None:
            return None
        object_id = obj['_id']
        result = {'object': object_name, 'batches': obj['batches']}

        def complement(b, batch_name):
            total_count = self.__load_articles_count(object_id, batch_name, verified_only)
            account_count, miss_principal_count = self.__load_articles_account_count(object_id, batch_name,
                                                                                     verified_only)
            b['total_count'] = total_count
            b['account_count'] = account_count
            b['miss_principal_count'] = miss_principal_count
            result['batches'][batch_name if len(batch_name) > 0 else 'NULL'] = b

        if len(batch) > 0:
            if 'batches' in result:
                batches = result['batches']
                if batch in batches:
                    complement(batches[batch], batch)
                    return result
        if 'batches' in result:
            batches = result['batches']
            for k, v in batches.items():
                complement(v, k)
        else:
            complement({}, '')
        return result

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

    def __load_articles_for_set(self, object_id):
        query = {'object_id': object_id}
        columns = {'_id': 0, 'title': 1, 'wechat_name': 1, 'time': 1}
        return self._db_articles.find(query, columns)

    def __update_object_info(self, object_id, last_index, batch, keyword, last_page, finished):
        query = {'_id': object_id}
        update = {'$set': {
            'last_index': last_index,
            'batches.' + batch + '.keywords.' + keyword: {
                'last_page': last_page,
                'finished': True if finished else False,
                'updated':  datetime.now()
            }
        }}
        return self._db_objects.update_one(query, update)

    def __load_articles_count(self, object_id, batch, verified_only):
        query = {'object_id': object_id}
        if len(batch) > 0:
            query['batch'] = batch
        if verified_only:
            query['isv'] = 1
        # if empty_principal:
        #     query['gzh.principal'] = ''
        return self._db_articles.count_documents(query)

    def __load_articles_account_count(self, object_id, batch, verified_only) -> (int, int):
        filter = {'object_id': object_id}
        if len(batch) > 0:
            filter['batch'] = batch
        if verified_only:
            filter['isv'] = 1
        ids = self._db_articles.distinct('gzh_id', filter)
        if len(ids) > 0:
            filter1 = {'_id': {'$in': ids}}
            total_count = self._db_accounts.count(filter1)
            filter2 = filter1
            filter2['detailed'] = 0
            miss_principal_count = self._db_accounts.count(filter2)
            return total_count, miss_principal_count
        return 0, 0

    @staticmethod
    def __dict_to_article(d) -> Article:
        account = Account()
        # gzh = d['gzh']
        # account.name = gzh['name']
        # account.avatar = gzh['avatar']
        # account.principal = gzh['principal']
        # account.wechat_id = gzh['wechat_id']
        # account.desc = gzh['desc']
        # account.qr_code = gzh['qr_code']
        article = Article(id=d['_id'],
                          index=d['index'],
                          title=d['title'],
                          url=d['url'],
                          temp_url=d['temp_url'],
                          time=d['time'],
                          wechat_name=d['wechat_name'],
                          profile_url=d['profile_url'],
                          isv=d['isv'],
                          gzh_id=d['gzh_id'],
                          # gzh=account,
                          )
        article.imgs = d['imgs']
        return article

    @staticmethod
    def __dict_to_account(d) -> Account:
        account = Account()
        account.id = d['_id']
        account.name = d['name']
        account.avatar = d['avatar']
        account.principal = d['principal']
        account.wechat_id = d['wechat_id']
        account.desc = d['desc']
        account.qr_code = d['qr_code']
        account.isv = d['isv']
        account.detailed = d['detailed']
        return account

    @staticmethod
    def __account_to_dict(account):
        return {
            'name': account.name,
            'avatar': account.avatar,
            'principal': account.principal,
            'wechat_id': account.wechat_id,
            'desc': account.desc,
            'qr_code': account.qr_code,
            'isv': account.isv,
            'detailed': account.detailed
        }
