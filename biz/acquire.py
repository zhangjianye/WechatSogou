import wechatsogou
from biz.datatype import Article, Account
from wechatsogou import WechatSogouAPI, WechatSogouConst, WechatSogouException
from wechatsogou.request import WechatSogouRequest
import time


def search_article(ws_api: WechatSogouAPI, keyword, page_limit=0, specified_page=0):
    def get_account_detail(a: Article):
        if len(a.profile_url) > 0:
            # time.sleep(5)
            # print('title={}, profile_url={}'.format(a.title, a.profile_url))
            try:
                result = ws_api.get_gzh_detail(a.profile_url)
                a.gzh.name = result['name']
                a.gzh.avatar = result['avatar']
                a.gzh.wechat_id = result['wechat_id'].removeprefix('微信号: ')
                a.gzh.desc = result['desc']
                a.gzh.principal = result['principal']
                a.gzh.qr_code = result['qr_code']
            except WechatSogouException as e:
                print(e)

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
            # time.sleep(5)
            article = Article()
            article.title = r['article']['title']
            article.url = r['article']['url']
            article.time = r['article']['time']
            article.profile_url = r['gzh']['profile_url']
            article.wechat_name = r['gzh']['wechat_name']
            article.isv = r['gzh']['isv']
            # if count == 6:
            #     print('aritcle.imgs={}'.format(r['article']['imgs']))
            for img in r['article']['imgs']:
                article.imgs.append(img)
            if len(article.url) > 0:
                # print('get_article_content with title={}'.format(article.title))
                try:
                    c = ws_api.get_article_content(article.url)
                    if c is not None: # and '该内容已被发布者删除' not in c['content_html']:
                        for item in c['content_img_list']:
                            article.imgs.append(item)
                    else:
                        continue
                except WechatSogouException:
                    print('article url expired, title={}, url={}'.format(article.title, article.url))
                    pass
            get_account_detail(article)
            articles.append(article)
            count += 1
            continue_search = has_next_page
        print('continue_search={}'.format(continue_search))
        if count == 0 or (0 < page_limit <= page) or specified_page > 0 or not continue_search:
            print('search end at page {}'.format(page))
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
