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
    usage: run.py -s -k <keyword> -o <object name> [-b <begin page>] [-e <end page>]
           run.py -c -k <key> -o <object name> [-b <begin index>] [-e <end index>]
           run.py -g -o <object name> -t <template id> [-f <filename>]
    """
    short_opts = 'hscgk:o:b:e:t:f:'
    long_opts = ['help', 'search', 'convert', 'generate', 'key=', 'object=', 'begin=', 'end=', 'template=', 'filename=']
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
            if 't' in args:
                conflicting = True
                break
            args['f'] = val
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
        __search(object_name, keywords, begin_page, end_page)
    elif args['m'] == 'c':
        keys = list(args['k'])
        begin_index = args['b'] if 'b' in args else 0
        end_index = args['e'] if 'e' in args else 0
        __convert(object_name, keys, begin_index, end_index)
    elif args['m'] == 'g':
        template = args['t']
        filename = args['f'] if 'f' in args else object_name
        __generate(object_name, template, filename)


def main(argv):
    __connect_db()
    args = __parse_argv(argv)
    print(args)
    __do(args)

    # workbook, sheet = output.prepare_excel('test', keyword)
    # page = 1
    continue_search = True
    # while (pages == 0 or page <= pages) and continue_search:
    #     articles, continue_search = acquire.search_article(ws_api, keyword, specified_page=page)
    #     if len(articles) > 0:
    #         process.process_qrcode(articles)
    #         result.extend(articles)
    #         # row = output.output_excel(workbook, sheet, articles, row)
    #     else:
    #         break
    #     page += 1

    # output.close_excel(workbook)


    # acquire.search_article(ws_api, keyword, page_limit=1)

    # articles = acquire.search_article(ws_api, keyword, specified_page=13)
    # output.output_excel(articles, 'test', keyword)

    # output.output_excel(None, None, 'test', keyword)


def __search(object_name, keywords, begin_page, end_page):
    assert len(keywords) > 0
    ws_api = WechatSogouAPI(captcha_break_time=19, keyword=keywords[0])
    articles_set = storage.Storage().load_article_set(object_name)
    # result = []

    def save(keyword, articles):
        storage.Storage().save_articles(object_name, keyword, articles)

    for k in keywords:
        __search_single_keyword(ws_api, k, begin_page, end_page, lambda x: save(k, x), articles_set)


def __search_single_keyword(ws_api, keyword, begin_page, end_page, save_method, article_set):
    page = begin_page
    continue_search = True
    while (page <= end_page or end_page == 0) and continue_search:
        articles, continue_search = acquire.search_article(ws_api, keyword, article_set, specified_page=page)
        if len(articles) > 0:
            process.process_qrcode(articles)
            save_method(articles)
            # result.extend(articles)
            # row = output.output_excel(workbook, sheet, articles, row)
        # else:
        #     break
        page += 1
    print('search {} end at page {}'.format(keyword, page - 1))


def __convert(object_name, keys, begin_index, end_index):
    articles = storage.Storage().load_articles(object_name, begin_index, end_index)
    converter = convert.Converter(keys)
    for a in articles:
        # if a
        pass


def __generate(object_name, template, filename):
    articles = storage.Storage().load_articles(object_name)
    output.output_html(object_name, filename, template, articles)
