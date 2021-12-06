from dataclasses import dataclass

import bson


@dataclass
class Account:
    id: bson.objectid = None
    name = ''
    avatar = ''
    principal = ''
    wechat_id = ''
    desc = ''
    qr_code = ''
    isv = 0
    detailed = 0

    def __repr__(self):
        return 'name=\'{}\', principal=\'{}\', wechat_id=\'{}\', desc=\'{}\''.format(self.name, self.principal, self.wechat_id, self.desc)


@dataclass
class Article:
    id: bson.ObjectId
    index: int
    title: str
    url: str
    temp_url: str
    time: int
    wechat_name: str
    profile_url: str
    isv: int
    gzh_id: bson.objectid
    gzh: Account
    imgs: []

    def __init__(self, id=None, index=0, title='', url='', temp_url='', time='', wechat_name='', profile_url='', isv=0, gzh=None):
        self.id = id
        self.index = index
        self.title = title
        self.url = url
        self.temp_url = temp_url
        self.time = time
        self.wechat_name = wechat_name
        self.profile_url = profile_url
        self.isv = isv
        self.gzh_id = None
        if gzh is None:
            self.gzh = Account()
        else:
            self.gzh = gzh
        self.imgs = []

    def __repr__(self):
        # return 'title=\'{}\', url=\'{}\', wechat_name=\'{}\''.format(self.title, self.url, self.wechat_name)
        return 'title=\'{}\', wechat_name=\'{}\', profile_url=\'{}\', gzh={{{}}}'.format(self.title, self.wechat_name, self.profile_url, self.gzh)

