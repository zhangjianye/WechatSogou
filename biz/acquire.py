import wechatsogou
from biz.datatype import Article, Account
from wechatsogou import WechatSogouAPI, WechatSogouConst, WechatSogouException
from wechatsogou.request import WechatSogouRequest
import time


def get_account_detail(ws_api: WechatSogouAPI, profile_url, gzh, wechat_name=''):
    if len(profile_url) > 0:
        # time.sleep(5)
        # print('title={}, profile_url={}'.format(a.title, a.profile_url))
        try:
            result = ws_api.get_gzh_detail(profile_url, wechat_name=wechat_name)
            if 'wechat_id' in result and len(result['wechat_id']) > 0:
                gzh.name = result.get('name', '')
                gzh.avatar = result.get('avatar', '')
                gzh.wechat_id = result.get('wechat_id', '').removeprefix('微信号: ')
                gzh.desc = result.get('desc', '')
                gzh.principal = result.get('principal', '')
                gzh.detailed = 1
                return True
        except WechatSogouException as e:
            print(e)
    return False


def search_article(ws_api: WechatSogouAPI, keyword, article_set, gzh_tester, gzh_saver, page_limit=0, specified_page=0):
    articles = []
    # images = {}
    # index = 0
    continue_search = False
    page = 1 if specified_page <= 0 else specified_page
    while True:
        count = 0
        # results = ws_api.search_article(keyword, page, article_type=WechatSogouConst.search_article_type.image)
        results = ws_api.search_article(keyword, page)
        for r, has_next_page in results:
            continue_search = has_next_page
            count += 1
            title = r['article']['title']
            wechat_name = r['gzh']['wechat_name']
            article_time = r['article']['time']
            combination = (title, wechat_name, article_time)
            if combination in article_set:
                print('article {} wrote by {} on {} existed'.format(title, wechat_name, article_time))
                continue
            else:
                article_set.add(combination)
            # time.sleep(5)
            article = Article()
            article.title = title
            article.temp_url = r['article']['url']
            article.time = article_time
            article.profile_url = r['gzh']['profile_url']
            article.wechat_name = wechat_name
            article.isv = r['gzh']['isv']
            # if count == 6:
            #     print('aritcle.imgs={}'.format(r['article']['imgs']))
            for img in r['article']['imgs']:
                article.imgs.append(img)
            if len(article.temp_url) > 0:
                # print('get_article_content with title={}'.format(article.title))
                try:
                    c = ws_api.get_article_content(article.temp_url)
                    if c is not None:  # and '该内容已被发布者删除' not in c['content_html']:
                        for item in c['content_img_list']:
                            article.imgs.append(item)
                    else:
                        continue
                except WechatSogouException:
                    print('article url expired, title={}, url={}'.format(article.title, article.temp_url))
                    pass
            gzh_id = gzh_tester(article.wechat_name)
            if gzh_id is None:
                gzh = article.gzh
                if not get_account_detail(ws_api, article.profile_url, gzh, article.wechat_name):
                    gzh.name = article.wechat_name
                gzh.isv = article.isv
                id = gzh_saver(gzh)
                article.gzh_id = id
            else:
                article.gzh_id = gzh_id

            articles.append(article)
        print('continue_search={}'.format(continue_search))
        if count == 0 or (0 < page_limit <= page) or specified_page > 0 or not continue_search:
            # print('search end at page {}'.format(page))
            break
        page += 1
    # for a in articles:
    #     if len(a.profile_url) > 0:
    #         # time.sleep(5)
    #         # print('title={}, profile_url={}'.format(a.title, a.profile_url))
    #         try:
    #             result = ws_api.get_gzh_detail(a.profile_url)
    #             a.gzh.name = result['name']
    #             a.gzh.avatar = result['avatar']
    #             a.gzh.wechat_id = result['wechat_id'].removeprefix('微信号: ')
    #             a.gzh.desc = result['desc']
    #             a.gzh.principal = result['principal']
    #             a.gzh.qr_code = result['qr_code']
    #         except WechatSogouException as e:
    #             print(e)
    return articles, continue_search
    # print(articles)
    # with open('/Users/zhangjianye/Downloads/test.txt', 'w') as f:
    #     print(articles, file=f)
    #     print(images, file=f)


def search_account(ws_api: WechatSogouAPI, name):
    info = ws_api.get_gzh_info(name)
    print(info)
    info = ws_api.get_gzh_article_by_history(name)
    print(info)


def search_list(ws_api: WechatSogouAPI, index, page_count):
    for page in range(1, page_count):
        info = ws_api.get_gzh_article_by_hot(index, page)
        for i in info:
            print('{}, {}'.format(i['gzh']['wechat_name'], i['article']['title']))
            try:
                c = ws_api.get_article_content(i['article']['url'])
                if c is not None:
                    print(c['content_img_list'])
            except WechatSogouException as e:
                print('******** exception occurred: {} ********'.format(e))
        print('page {}, get {} articles'.format(page, len(info)))
        print('======================================')


def replenish_gzh(ws_api: WechatSogouAPI, account: Account) -> bool:
    gzhs = ws_api.search_gzh(account.name if len(account.wechat_id) == 0 else account.wechat_id)
    profile_url = ''
    for gzh in gzhs:
        if gzh['wechat_id'] == account.wechat_id or gzh['wechat_name'] == account.name:
            profile_url = gzh['profile_url']
            account.wechat_id = gzh.get('wechat_id', account.wechat_id)
            account.name = gzh.get('wechat_name', account.name)
            account.principal = gzh.get('authentication', account.principal)
            account.avatar = gzh.get('headimage', account.avatar)
            account.desc = gzh.get('introduction', account.desc)
            account.detailed = 1
            break
    # if len(article.gzh.principal) == 0 or len(article.gzh.name) == 0:
    #     return get_account_detail(ws_api, profile_url, article.gzh)
    return True
