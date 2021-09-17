# -*- coding: utf-8 -*-

from biz import acquire, output, process
from wechatsogou import WechatSogouAPI, WechatSogouConst


def main():

    # hot_index = WechatSogouConst.hot_index.hot
    # search_list(ws_api, hot_index, 1)

    keywords = []
    while len(keywords) <= 0:
        keywords = input('Enter keywords:').split()

    pages_str = input('Enter page count:')
    try:
        pages = int(pages_str)
    except:
        pages = 0
    keyword = keywords[0]
    ws_api = WechatSogouAPI(captcha_break_time=19, keyword=keyword)
    # workbook, sheet = output.prepare_excel('test', keyword)
    # page = 1
    result = []
    for k in keywords:
        __search(ws_api, k, pages, result)
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

    output.output_html(keyword, keyword, result)

    # acquire.search_article(ws_api, keyword, page_limit=1)

    # articles = acquire.search_article(ws_api, keyword, specified_page=13)
    # output.output_excel(articles, 'test', keyword)

    # output.output_excel(None, None, 'test', keyword)


def __search(ws_api, keyword, pages, result):
    page = 1
    continue_search = True
    while (pages == 0 or page <= pages) and continue_search:
        articles, continue_search = acquire.search_article(ws_api, keyword, specified_page=page)
        if len(articles) > 0:
            process.process_qrcode(articles)
            result.extend(articles)
            # row = output.output_excel(workbook, sheet, articles, row)
        else:
            break
        page += 1
