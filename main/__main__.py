# -*- coding: utf-8 -*-

from biz import acquire as acquire
from biz import output as output
from wechatsogou import WechatSogouAPI, WechatSogouConst


def main():
    ws_api = WechatSogouAPI(captcha_break_time=3)
    hot_index = WechatSogouConst.hot_index.hot
    # search_list(ws_api, hot_index, 1)
    keyword = input('Enter keyword:')
    articles = acquire.search_article(ws_api, keyword, 1)
    output.output_excel(articles, 'test', keyword)
    # output.output_excel(None, None, 'test', keyword)
