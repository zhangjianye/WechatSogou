# -*- coding: utf-8 -*-

from biz import acquire as acquire
from biz import output as output
from wechatsogou import WechatSogouAPI, WechatSogouConst


def main():

    # hot_index = WechatSogouConst.hot_index.hot
    # search_list(ws_api, hot_index, 1)

    keyword = input('Enter keyword:')
    pages_str = input('Enter page count:')
    try:
        pages = int(pages_str)
    except:
        pages = 0
    ws_api = WechatSogouAPI(captcha_break_time=19, keyword=keyword)
    workbook, sheet = output.prepare_excel('test', keyword)
    page = 1
    row = 1
    while pages == 0 or page <= pages:
        articles = acquire.search_article(ws_api, keyword, specified_page=page)
        if len(articles) > 0:
            row = output.output_excel(workbook, sheet, articles, row)
        else:
            break
        page += 1

    output.close_excel(workbook)

    # acquire.search_article(ws_api, keyword, page_limit=1)

    # articles = acquire.search_article(ws_api, keyword, specified_page=13)
    # output.output_excel(articles, 'test', keyword)

    # output.output_excel(None, None, 'test', keyword)
