import pymongo
import pymongo.errors
from datetime import datetime


class Migrator:
    def __init__(self, connection_string=''):
        mongo_client = pymongo.MongoClient(connection_string)
        try:
            _ = mongo_client.server_info()
            mongo_db = mongo_client['wechat']
            self._db_articles = mongo_db['articles']
            self._db_objects = mongo_db['objects']
            self._db_accounts = mongo_db['accounts']
            self._connected = True
            self._version = 2
            self._accounts = {}
        except pymongo.errors.PyMongoError as err:
            print("connect to mongodb {} failed, err: {}".format(connection_string, err))
            self._db_articles = None
            self._db_objects = None
            self._connected = False

    def migrate(self):
        self.pre_load_accounts()
        query = {'$or': [{'version': None}, {'version': {'$lt': 2}}]}
        while True:
            articles = self._db_articles.find(query).limit(2000)
            count = 0
            for a in articles:
                gzh = self._accounts.get(a['wechat_name'])
                if gzh is None:
                    gzh = a['gzh']
                    gzh['isv'] = a['isv']
                    if len(gzh['name']) == 0:
                        gzh['name'] = a['wechat_name']
                    a['gzh_id'] = self.insert_account(gzh)
                else:
                    a['gzh_id'] = gzh['_id']
                    gzh_new = a['gzh']
                    if len(gzh_new['name']) == 0:
                        gzh_new['name'] = a['wechat_name']
                    if self.merge_account(gzh, gzh_new):
                        self.update_account(gzh)
                self.save_article(a)
                self.update_object(a['object_id'], a['keyword'])
                count += 1
            if count == 0:
                break
            print('{} articles migrated.'.format(count))
        print('migration finished.')

    def pre_load_accounts(self):
        accounts = self._db_accounts.find({})
        for a in accounts:
            self._accounts[a['name']] = a

    def save_article(self, article):
        del(article['gzh'])
        article['version'] = self._version
        article['batch'] = 'default'
        self._db_articles.replace_one({'_id': article['_id']}, article)

    def load_account(self, name):
        return self._db_accounts.find_one({'name': name})

    def insert_account(self, gzh):
        gzh['version'] = self._version
        gzh['detailed'] = 1 if len(gzh['wechat_id']) > 0 else 0
        self._accounts[gzh['name']] = gzh
        return self._db_accounts.insert_one(gzh).inserted_id

    def update_account(self, gzh):
        self._db_accounts.replace_one({'_id': gzh['_id']}, gzh)

    def update_object(self, object_id, keyword):
        query = {'_id': object_id}
        obj = self._db_objects.find_one(query)
        if 'batches' not in obj or 'default' not in obj['batches'] or keyword not in obj['batches']['default']['keywords']:
            update = {'$set': {
                'version': self._version,
                'batches.default.keywords.' + keyword: {
                    'last_page': 0,
                    'finished': True,
                    'updated': datetime.now()
                }
            }}
            self._db_objects.update_one(query, update)

    @staticmethod
    def merge_account(gzh_dest, gzh_src):
        detailed_dest = gzh_dest['detailed']
        detailed_src = 1 if len(gzh_src['wechat_id']) > 0 else 0
        if detailed_dest == 0 and detailed_src == 1:
            gzh_dest |= gzh_src
            gzh_src['detailed'] = 1
            return True
        elif detailed_dest == 1 and detailed_src == 1:
            changed = False
            if len(gzh_src['name']) > len(gzh_dest['name']):
                gzh_dest['name'] = gzh_src['name']
                changed = True
            if len(gzh_src['avatar']) > len(gzh_src['avatar']):
                gzh_dest['avatar'] = gzh_src['avatar']
                changed = True
            if len(gzh_src['principal']) > len(gzh_src['principal']):
                gzh_dest['principal'] = gzh_src['principal']
                changed = True
            if len(gzh_src['desc']) > len(gzh_src['desc']):
                gzh_dest['desc'] = gzh_src['desc']
                changed = True
            if len(gzh_src['qr_code']) > len(gzh_src['qr_code']):
                gzh_dest['qr_code'] = gzh_src['qr_code']
                changed = True
            return changed
        else:
            return False


# connection_string = 'mongodb://127.0.0.1:27017'
connection_string = 'mongodb://root:09wnLij9vFtHRZCy@official-accounts.mongodb.rds.aliyuncs.com:3717'
Migrator(connection_string).migrate()
