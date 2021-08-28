from dataclasses import dataclass


@dataclass
class Account:
    avatar = ''
    principal = ''
    wechat_id = ''
    desc = ''
    qr_code = ''

    def __repr__(self):
        return 'principal=\'{}\', wechat_id=\'{}\', desc=\'{}\''.format(self.principal, self.wechat_id, self.desc)


@dataclass
class Article:
    title: str
    url: str
    time: int
    wechat_name: str
    profile_url: str
    isv: int
    gzh: Account
    imgs: []

    def __init__(self, title='', url='', time='', wechat_name='', profile_url='', isv=0, gzh=None):
        self.title = title
        self.url = url
        self.time = time
        self.wechat_name = wechat_name
        self.profile_url = profile_url
        self.isv = isv
        if gzh is None:
            self.gzh = Account()
        else:
            self.gzh = gzh
        self.imgs = []

    def __repr__(self):
        # return 'title=\'{}\', url=\'{}\', wechat_name=\'{}\''.format(self.title, self.url, self.wechat_name)
        return 'title=\'{}\', wechat_name=\'{}\', profile_url=\'{}\', gzh={{{}}}'.format(self.title, self.wechat_name, self.profile_url, self.gzh)

