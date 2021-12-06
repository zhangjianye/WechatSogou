# -*- coding: utf-8 -*-
import getopt
import sys

from biz import acquire, output, process, storage, convert
from wechatsogou import WechatSogouAPI
from common import tools


def __connect_db():
    connection_string = 'mongodb://127.0.0.1:27017'
    # connection_string = 'mongodb://root:09wnLij9vFtHRZCy@official-accounts.mongodb.rds.aliyuncs.com:3717'
    if not storage.Storage(connection_string).connected():
        print('connect to db {} failed.'.format(connection_string))
        sys.exit(1)


def __parse_argv(argv):
    args = {}
    usage = """
    usage: wx.exe -s -k <keyword> -o <object name> [-b <begin page>] [-e <end page>] [-a <batch name>]
           wx.exe -c -k <key> -o <object name> [-b <begin index>] [-e <end index>]  [-a <batch name>]
           wx.exe -g -o <object name> -t <template id> [-f <filename>] [-b <begin index>] [-e <end index>]  [-a <batch name>]
           wx.exe -r -o <object name>  [-a <batch name>]
           wx.exe -i -o <object name>  [-a <batch name>]
    """
    short_opts = 'hscgrik:o:b:e:t:f:a:'
    long_opts = ['help', 'search', 'convert', 'generate', 'replenish', 'information', 'key=', 'object=', 'begin=',
                 'end=', 'template=', 'filename=', 'batch=']
    try:
        opts, values = getopt.getopt(argv, short_opts, long_opts)
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    conflicting = False
    for arg, val in opts:
        if arg in ('-h', '--help'):
            if 'm' in args:
                conflicting = True
                break
            args['m'] = 'h'
        elif arg in ('-s', '--search'):
            if 'm' in args:
                conflicting = True
                break
            args['m'] = 's'
        elif arg in ('-c', '--convert'):
            if 'm' in args:
                conflicting = True
                break
            args['m'] = 'c'
        elif arg in ('-g', '--generate'):
            if 'm' in args:
                conflicting = True
                break
            args['m'] = 'g'
        elif arg in ('-k', '--key'):
            vals = val.split()
            if 'k' not in args:
                args['k'] = set()
            for v in vals:
                args['k'].add(v)
        elif arg in ('-o', '--object'):
            if 'o' in args:
                conflicting = True
                break
            args['o'] = val
        elif arg in ('-b', '--begin'):
            if 'b' in args:
                conflicting = True
                break
            args['b'] = tools.atoi(val)
        elif arg in ('-e', '--end'):
            if 'e' in args:
                conflicting = True
                break
            args['e'] = tools.atoi(val)
        elif arg in ('-t', '--template'):
            if 't' in args:
                conflicting = True
                break
            args['t'] = val
        elif arg in ('-f', '--filename'):
            if 'f' in args:
                conflicting = True
                break
            args['f'] = val
        elif arg in ('-r', '--replenish'):
            if 'm' in args:
                conflicting = True
                break
            args['m'] = 'r'
        elif arg in ('-i', '--information'):
            if 'm' in args:
                conflicting = True
                break
            args['m'] = 'i'
        elif arg in ('-a', '--batch'):
            if 'a' in args:
                conflicting = True
                break
            args['a'] = val
    if conflicting:
        print('arguments conflicted.')
        print(usage)
        sys.exit(2)
    valid = True
    if 'm' not in args or 'o' not in args:
        valid = False
    elif args['m'] in ('s', 'c') and 'k' not in args:
        valid = False
    elif args['m'] == 'g' and 't' not in args:
        valid = False
    if not valid:
        print('some arguments are missed.')
        print(usage)
        sys.exit(2)
    return args


def __do(args):
    object_name = args['o']
    if args['m'] == 's':
        keywords = list(args['k'])
        begin_page = args['b'] if 'b' in args else 1
        if begin_page < 1:
            begin_page = 1
        end_page = args['e'] if 'e' in args else 0
        batch = args['a'] if 'a' in args else 'default'
        __search(object_name, keywords, begin_page, end_page, batch)
    elif args['m'] == 'c':
        keys = list(args['k'])
        begin_index = args['b'] if 'b' in args else 0
        end_index = args['e'] if 'e' in args else 0
        batch = args['a'] if 'a' in args else 'default'
        __convert(object_name, keys, begin_index, end_index, batch)
    elif args['m'] == 'g':
        template = args['t']
        filename = args['f'] if 'f' in args else object_name
        begin_index = args['b'] if 'b' in args else 0
        end_index = args['e'] if 'e' in args else 0
        batch = args['a'] if 'a' in args else 'default'
        __generate(object_name, template, filename, begin_index, end_index, batch)
    elif args['m'] == 'r':
        batch = args['a'] if 'a' in args else 'default'
        __replenish(object_name, batch)
    elif args['m'] == 'i':
        batch = args['a'] if 'a' in args else ''
        __information(object_name, batch)


def main(argv):
    __connect_db()
    args = __parse_argv(argv)
    print(args)
    __do(args)


def __search(object_name, keywords, begin_page, end_page, batch):
    assert len(keywords) > 0
    need_login = True
    if 0 < end_page <= 10:
        need_login = False
    ws_api = WechatSogouAPI(captcha_break_time=5, keyword=keywords[0], need_login=need_login)
    articles_set = storage.Storage().load_article_set(object_name)

    # result = []

    def save(keyword, articles, page, finished):
        storage.Storage().save_articles(object_name, keyword, articles, batch, page, finished)

    for k in keywords:
        __search_single_keyword(ws_api, k, begin_page, end_page, lambda x, y, z: save(k, x, y, z), articles_set)


def __search_single_keyword(ws_api, keyword, begin_page, end_page, save_method, article_set):
    page = begin_page
    continue_search = True

    def test_gzh(name):
        return storage.Storage().test_account(name)

    def save_gzh(gzh):
        storage.Storage().save_account(gzh)
        return gzh.id

    while (page <= end_page or end_page == 0) and continue_search:
        articles, continue_search = acquire.search_article(ws_api, keyword, article_set, test_gzh, save_gzh,
                                                           specified_page=page)
        if len(articles) > 0:
            process.process_qrcode(articles)
            save_method(articles, page, not continue_search)
            # result.extend(articles)
            # row = output.output_excel(workbook, sheet, articles, row)
        # else:
        #     break
        page += 1
    print('search {} end at page {}'.format(keyword, page - 1))


def __convert(object_name, keys, begin_index, end_index, batch):
    articles = storage.Storage().load_articles(object_name, begin_index, end_index, empty_url=True, batch=batch)
    converter = convert.Converter(keys)
    converter.convert(articles, lambda x: storage.Storage().update_article_url(x))
    # for a in articles:
    #     if len(a.url) > 0:
    #         continue
    #     if len(a.temp_url) > 0:
    #         try:
    #             a.url = converter.convert(a.temp_url)
    #             storage.Storage().update_article_url(a)
    #         except convert.ConvertException as e:
    #             print('convert exception occurred, object={}, index={}, e={}', object_name, a.index, e)
    #             break


def __generate(object_name, template, filename, begin_index, end_index, batch):
    articles = storage.Storage().load_articles(object_name, begin_index, end_index, batch=batch, expand_account=True)
    output.output_html(object_name, filename, template, articles)


def __replenish(object_name, batch):
    ws_api = WechatSogouAPI(captcha_break_time=5, need_login=False)
    articles = storage.Storage().load_articles(object_name, batch=batch, expand_account=True)

    def save(account):
        storage.Storage().save_account(account)

    for article in articles:
        if article.gzh.detailed == 0:
            if acquire.replenish_gzh(ws_api, article.gzh):
                print('article {} replenished gzh succeed, gzh = {}'.format(article, article.gzh))
                save(article.gzh)


def __information(object_name, batch):
    info = storage.Storage().load_object_info(object_name, batch)
    if info is None:
        print('{} not found'.format(object_name))
        return
    print('object :{}'.format(object_name))
    if 'batches' in info:
        for k, v in info['batches'].items():
            print('    batch {}:'.format(k))
            if 'keywords' in v:
                for k1, v1 in v['keywords'].items():
                    print('        keyword {}, last page: {}, finished: {}'.format(k1, v1['last_page'],
                                                                                   'YES' if v1['finished'] else 'NO'))
            print('        total count: {}'.format(v['total_count']))
            print('        miss-principal count: {}'.format(v['miss_principal_count']))
