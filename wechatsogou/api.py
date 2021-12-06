# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import selenium.common.exceptions
from selenium import webdriver
import json
import math
import random
import re
import time
from pathlib import Path
import requests

from wechatsogou.const import agents, WechatSogouConst
from wechatsogou.exceptions import WechatSogouException, WechatSogouRequestsException, WechatSogouVcodeOcrException, \
    WechatSogouVcodeOcrLimitedException
from wechatsogou.five import must_str, quote
from wechatsogou.identify_image import (identify_image_callback_by_hand, identify_image_callback_automatically,
                                        unlock_sogou_callback_example, unlock_weixin_callback_example, ws_cache)
from wechatsogou.request import WechatSogouRequest
from wechatsogou.structuring import WechatSogouStructuring
from wechatsogou.tools import may_int

import os


class WechatSogouAPI(object):
    def __init__(self, captcha_break_time=1, headers=None, cookies=None, keyword='', need_login=True, **kwargs):
        """初始化参数

        Parameters
        ----------
        captcha_break_time : int
            验证码输入错误重试次数
        proxies : dict
            代理
        timeout : float
            超时时间
        """
        assert isinstance(captcha_break_time, int) and 0 < captcha_break_time < 20

        self.captcha_break_times = captcha_break_time
        self.requests_kwargs = kwargs
        self.headers = headers
        self.cookies = cookies
        self.need_login = need_login
        if self.cookies is None:
            self.cookies = {}
        if self.headers:
            self.headers['User-Agent'] = random.choice(agents)
        else:
            self.headers = {'User-Agent': random.choice(agents)}
        self.session = None
        self.keyword = keyword
        if len(self.keyword) == 0:
            self.keyword = '百度'
        self.prepare_wechat_environment()

    def reset_session(self):
        self.cookies.clear()
        self.prepare_wechat_environment()

    def prepare_wechat_environment(self):
        '''
        Login wechat by automatically inputing accounts and keywords and manully scanning QR code， and then you can
        get the cookie information, save it in local file in order to simulate loginning and crawling……
        :param __username:
        :param __password:
        :return:
        '''
        print("浏览器将自动打开并跳转至微信公众号登录页面……")
        time.sleep(1)
        driver = webdriver.Chrome()
        driver.get("https://weixin.sogou.com/")
        time.sleep(2)
        if self.need_login:
            login_button = driver.find_element_by_id('loginBtn')
            if login_button:
                login_button.click()
        # print("正在自动输入账号、密码......请勿操作")
        # driver.find_element_by_name("account").clear()
        # driver.find_element_by_name("account").send_keys(self.__username)
        # time.sleep(1)
        # driver.find_element_by_name("password").clear()
        # driver.find_element_by_name("password").send_keys(self.__password)
        # time.sleep(1)
        # driver.find_element_by_class_name("frm_checkbox_label").click()
        # time.sleep(2)
        # driver.find_element_by_class_name("btn_login").click()
        print("请拿手机扫码二维码登录公众号")
        count = 0
        while True:
            if self.need_login:
                time.sleep(3)
                try:
                    login_yes = driver.find_element_by_id('login_yes')
                    if login_yes:
                        if login_yes.is_displayed():
                            print("登录成功")
                            # break
                        else:
                            continue
                except selenium.common.exceptions.WebDriverException:
                    continue

            try:
                time.sleep(2)
                query = driver.find_element_by_id('query')
                commit = driver.find_element_by_xpath('//input[@uigs="search_article"]')
                if query and commit:
                    query.send_keys(self.keyword)
                    commit.click()
                    while True:
                        text = driver.page_source
                        if '请输入验证码' in text:
                            time.sleep(5)
                        else:
                            break
                    break

            except selenium.common.exceptions.WebDriverException:
                pass

            # count += 1
            # if count >= 5:
            #     print("可能登录成功")
            #     break
        time.sleep(2)
        user_agent = driver.execute_script("return navigator.userAgent;")
        print('user-agent:{}'.format(user_agent))
        if user_agent:
            self.headers['User-Agent'] = user_agent
        cookies = driver.get_cookies()
        print(cookies)
        info = {}
        for cookie in cookies:
            cookie_name = cookie['name']
            cookie_value = cookie['value']
            if (cookie_name == 'ppmdig' or cookie_name == 'ABTEST') and cookie['domain'] != 'weixin.sogou.com':
                continue
            if cookie_name in info:
                info[cookie_name].add(cookie_value)
            else:
                info[cookie_name] = {cookie_value}
        self.cookies = info
        print(self.cookies)
        print(self.__get_cookie())

        # time.sleep(30 * 60)

        # cookie_info = json.dumps(info)
        # with open(self.cookie_path, 'w+', encoding='utf-8') as f:
        #     f.write(cookie_info)
        #     f.flush()
        # print("cookies已存入cookie.txt", flush=True)

        driver.quit()

        # prepare JSESSIONID
        # url = 'https://weixin.sogou.com/'
        # session = self.__get_session()
        # headers = self.__set_cookie()
        # resp = self.__get(url, session, headers=headers)
        # self.__get_jsessionid(resp.url)

    def __get_jsessionid(self, referer):
        if 'JSESSIONID' not in self.cookies:
            url = "https://weixin.sogou.com/websearch/wexinurlenc_sogou_profile.jsp"
            session = self.__get_session()
            headers = self.__set_cookie(referer=referer)
            resp = self.__get(url, session, headers=headers)
            print('Set-Cookie:')
            print(resp.headers['Set-Cookie'])
            print('session.cookies.JSESSIONID={}'.format(session.cookies.get('JSESSIONID')))
            jsessionId = session.cookies.get('JSESSIONID')
            if jsessionId:
                self.__redact_cookie('JSESSIONID', jsessionId)

    def __get_cookie(self):
        if self.cookies:
            l = []
            for key, values in self.cookies.items():
                for v in values:
                    l.append('{}={}'.format(key, v))
            return '; '.join(l)
        return ''

    def __redact_cookie(self, name, value):
        if name in self.cookies:
            self.cookies[name].add(value)
        else:
            self.cookies[name] = {value}

    def __set_cookie(self, suv=None, snuid=None, referer=None):
        suv = ws_cache.get('suv') if suv is None else suv
        snuid = ws_cache.get('snuid') if snuid is None else snuid
        _headers = {}
        if not self.cookies:
            print('cookies is empty')
            _headers['Cookie'] = 'SUV={};SNUID={};'.format(suv, snuid)
        else:
            # print('cookies is not empty')
            cookies = self.__get_cookie()
            # print(cookies)
            _headers['Cookie'] = cookies
        if referer is not None:
            _headers['Referer'] = referer
        # print('headers:')
        # print(_headers)
        return _headers

    def __get_session(self):
        if self.session is None:
            self.session = requests.session()
        return self.session

    def __set_cache(self, suv, snuid):
        ws_cache.set('suv', suv)
        ws_cache.set('snuid', snuid)

    def __get(self, url, session, headers):
        h = {}
        if headers:
            for k, v in headers.items():
                h[k] = v
        if self.headers:
            for k, v in self.headers.items():
                h[k] = v
        print('__get, url={}, headers={}'.format(url, h))
        try:
            resp = session.get(url, headers=h, **self.requests_kwargs)
        except Exception as e:
            raise WechatSogouRequestsException(e)

        if not resp.ok:
            raise WechatSogouRequestsException('WechatSogouAPI get error', resp)

        return resp

    def __unlock_sogou(self, url, resp, session, unlock_callback=None, identify_image_callback=None):
        if unlock_callback is None:
            unlock_callback = unlock_sogou_callback_example
        millis = int(round(time.time() * 1000))
        captcha_url = 'https://weixin.sogou.com/antispider/util/seccode.php?tc={}'.format(millis)
        r_captcha = session.get(captcha_url, headers={
            'Referer': url,
        })
        print('__unlock_sogou, url={}, ref={}'.format(captcha_url, url))
        if not r_captcha.ok:
            raise WechatSogouRequestsException('WechatSogouAPI get img', r_captcha)

        r_unlock, code = unlock_callback(url, session, resp, r_captcha.content, identify_image_callback)

        if r_unlock['code'] != 0:
            self.__write_failed_verified_image(code, r_captcha.content)
            print(r_unlock)
            raise WechatSogouVcodeOcrException(
                '[WechatSogouAPI identify image] code: {code}, msg: {msg}'.format(code=r_unlock.get('code'),
                                                                                  msg=r_unlock.get('msg')))
        else:
            self.__set_cache(session.cookies.get('SUID'), r_unlock['id'])

    def __unlock_wechat(self, url, resp, session, unlock_callback=None, identify_image_callback=None):
        if unlock_callback is None:
            unlock_callback = unlock_weixin_callback_example

        r_captcha = session.get('https://mp.weixin.qq.com/mp/verifycode?cert={}'.format(time.time() * 1000))
        if not r_captcha.ok:
            raise WechatSogouRequestsException('WechatSogouAPI unlock_history get img', resp)

        r_unlock, code = unlock_callback(url, session, resp, r_captcha.content, identify_image_callback)

        ret = r_unlock['ret']
        if ret != 0:
            self.__write_failed_verified_image(code, r_captcha.content)
            print(r_unlock)
            if ret == -6:
                raise WechatSogouVcodeOcrLimitedException(
                    '[WechatSogouAPI identify image] code: {ret}, msg: {errmsg}, cookie_count: {cookie_count}'.format(
                        ret=r_unlock.get('ret'), errmsg=r_unlock.get('errmsg'),
                        cookie_count=r_unlock.get('cookie_count')))
            else:
                raise WechatSogouVcodeOcrException(
                    '[WechatSogouAPI identify image] code: {ret}, msg: {errmsg}, cookie_count: {cookie_count}'.format(
                        ret=r_unlock.get('ret'), errmsg=r_unlock.get('errmsg'),
                        cookie_count=r_unlock.get('cookie_count')))

    @staticmethod
    def __write_failed_verified_image(code, content):
        directory = os.path.join(os.getcwd(), 'temp')
        Path(directory).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(directory, code + '.jpeg'), 'wb') as file:
            file.write(content)

    def __get_by_unlock(self, url, referer=None, unlock_platform=None, unlock_callback=None,
                        identify_image_callback=None, session=None):
        assert unlock_platform is None or callable(unlock_platform)

        if identify_image_callback is None:
            identify_image_callback = identify_image_callback_automatically
        assert unlock_callback is None or callable(unlock_callback)
        assert callable(identify_image_callback)
        retry_times = 0
        while True:
            if not session:
                session = self.__get_session()
            headers = self.__set_cookie(referer=referer)
            # print('================__get_by_unlock({})================='.format(url))
            # print('headers:{}'.format(headers))
            # print('url:{}'.format(url))
            # print('referer:{}'.format(referer))
            resp = self.__get(url, session, headers=headers)
            # print('resp.url = {}'.format(resp.url))
            # print('resp.text = {}'.format(resp.text))

            # print('Set-Cookie:')
            # print(resp.headers['Set-Cookie'])
            # print('session.cookies.SNUID={}'.format(session.cookies.get('SNUID')))
            # print('resp.cookies.SNUID={}'.format(resp.cookies.get('SNUID')))
            snuid = session.cookies.get('SNUID')
            if snuid:
                self.__redact_cookie('SNUID', snuid)
            self.__get_jsessionid(resp.url)
            resp.encoding = 'utf-8'
            if 'antispider' in resp.url or '请输入验证码' in resp.text:
                print("before unlock_platform, url={}".format(resp.url))
                # print('resp.txt={}'.format(resp.text))
                i = 0
                manual = False
                while manual or i < self.captcha_break_times:
                    try:
                        unlock_platform(url=url, resp=resp, session=session, unlock_callback=unlock_callback,
                                        identify_image_callback=identify_image_callback)
                        break
                    except WechatSogouVcodeOcrLimitedException as e:
                        raise e
                    except (WechatSogouVcodeOcrException, WechatSogouRequestsException) as e:
                        if i == self.captcha_break_times - 1:
                            # if not manual:
                            #     manual = True
                            #     i = -1
                            #     identify_image_callback = identify_image_callback_by_hand
                            # else:
                            raise WechatSogouVcodeOcrException(e)
                    i += 1
                    # else:
                    #     time.sleep(0.05)
                time.sleep(1)
                # if '请输入验证码' in resp.text:
                #     resp = session.get(url)
                #     resp.encoding = 'utf-8'
                # else:
                if 'antispider' in resp.url:
                    headers = self.__set_cookie(referer=referer)
                    # headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64)'
                    resp = self.__get(url, session, headers)
                    resp.encoding = 'utf-8'
                else:
                    resp = session.get(url)
                    resp.encoding = 'utf-8'
                print("after unlock_platform, url={}".format(resp.url))
                if '请输入验证码' in resp.text:
                    print('*******what the fuck, text begin******')
                    print(resp.text)
                    print('*******what the fuck, text end******')
                    retry_times += 1
                    if retry_times >= 2:
                        break
                else:
                    break
            else:
                break
        return resp

    def __hosting_wechat_img(self, content_info, hosting_callback):
        """将微信明细中图片托管到云端，同时将html页面中的对应图片替换

        Parameters
        ----------
        content_info : dict 微信文章明细字典
            {
                'content_img_list': [], # 从微信文章解析出的原始图片列表
                'content_html': '', # 从微信文章解析出文章的内容
            }
        hosting_callback : callable
            托管回调函数，传入单个图片链接，返回托管后的图片链接

        Returns
        -------
        dict
            {
                'content_img_list': '', # 托管后的图片列表
                'content_html': '',  # 图片链接为托管后的图片链接内容
            }
        """
        assert callable(hosting_callback)

        content_img_list = content_info.pop("content_img_list")
        content_html = content_info.pop("content_html")
        for idx, img_url in enumerate(content_img_list):
            hosting_img_url = hosting_callback(img_url)
            if not hosting_img_url:
                # todo 定义标准异常
                raise Exception()
            content_img_list[idx] = hosting_img_url
            content_html = content_html.replace(img_url, hosting_img_url)

        return dict(content_img_list=content_img_list, content_html=content_html)

    def __format_url(self, url, referer, text, unlock_callback=None, identify_image_callback=None, session=None):
        def _parse_url(url, pads):
            b = math.floor(random.random() * 100) + 1
            a = url.find("url=")
            c = url.find("&k=")
            if a != -1 and c == -1:
                sum = 0
                for i in list(pads) + [a, b]:
                    sum += int(must_str(i))
                a = url[sum]

            return '{}&k={}&h={}'.format(url, may_int(b), may_int(a))

        if url.startswith('/link?url='):
            url = 'https://weixin.sogou.com{}'.format(url)

            pads = re.findall(r'href\.substr\(a\+(\d+)\+parseInt\("(\d+)"\)\+b,1\)', text)
            url = _parse_url(url, pads[0] if pads else [])
            print('in __format_url, before __get_by_unlock, url={}'.format(url))
            try:
                resp = self.__get_by_unlock(url,
                                            referer=referer,
                                            unlock_platform=self.__unlock_sogou,
                                            unlock_callback=unlock_callback,
                                            identify_image_callback=identify_image_callback,
                                            session=session)
            except WechatSogouException as e:
                print(e)
                return url
            uri = ''
            base_url = re.findall(r'var url = \'(.*?)\';', resp.text)
            if base_url and len(base_url) > 0:
                uri = base_url[0]

            mp_url = re.findall(r'url \+= \'(.*?)\';', resp.text)
            if mp_url:
                uri = uri + ''.join(mp_url)
            url = uri.replace('@', '')
            if len(url) == 0:
                print('======text start=================================')
                print(resp.text)
                print('======text end=================================')
        return url

    def get_gzh_info(self, wecgat_id_or_name, unlock_callback=None, identify_image_callback=None, decode_url=True):
        """获取公众号微信号 wechatid 的信息

        因为wechatid唯一确定，所以第一个就是要搜索的公众号

        Parameters
        ----------
        wecgat_id_or_name : str or unicode
            wechat_id or wechat_name
        unlock_callback : callable
            处理出现验证码页面的函数，参见 unlock_callback_example
        identify_image_callback : callable
            处理验证码函数，输入验证码二进制数据，输出文字，参见 identify_image_callback_example

        Returns
        -------
        dict or None
            {
                'open_id': '', # 微信号唯一ID
                'profile_url': '',  # 最近10条群发页链接
                'headimage': '',  # 头像
                'wechat_name': '',  # 名称
                'wechat_id': '',  # 微信id
                'post_perm': '',  # 最近一月群发数
                'qrcode': '',  # 二维码
                'introduction': '',  # 介绍
                'authentication': ''  # 认证
            }
        """
        info = self.search_gzh(wecgat_id_or_name, 1, unlock_callback, identify_image_callback, decode_url)
        try:
            return next(info)
        except StopIteration:
            return None

    def search_gzh(self, keyword, page=1, unlock_callback=None, identify_image_callback=None, decode_url=True):
        """搜索 公众号

        对于出现验证码的情况，可以由使用者自己提供：
            1、函数 unlock_callback ，这个函数 handle 出现验证码到解决的整个流程
            2、也可以 只提供函数 identify_image_callback，这个函数输入验证码二进制数据，输出验证码文字，剩下的由 wechatsogou 包来解决
        注意：
            函数 unlock_callback 和 identify_image_callback 只需要提供一个，如果都提供了，那么 identify_image_callback 不起作用

        Parameters
        ----------
        keyword : str or unicode
            搜索文字
        page : int, optional
            页数 the default is 1
        unlock_callback : callable
            处理出现验证码页面的函数，参见 unlock_callback_example
        identify_image_callback : callable
            处理验证码函数，输入验证码二进制数据，输出文字，参见 identify_image_callback_example
        decode_url : bool
            是否解析 url

        Returns
        -------
        list[dict]
            {
                'open_id': '', # 微信号唯一ID
                'profile_url': '',  # profile
                'headimage': '',  # 头像
                'wechat_name': '',  # 名称
                'wechat_id': '',  # 微信id
                'post_perm': '',  # 最近一月群发数
                'qrcode': '',  # 二维码
                'introduction': '',  # 介绍
                'authentication': ''  # 认证
            }

        Raises
        ------
        WechatSogouRequestsException
            requests error
        """
        url = WechatSogouRequest.gen_search_gzh_url(keyword, page)
        session = self.__get_session()
        try:
            resp = self.__get_by_unlock(url,
                                    unlock_platform=self.__unlock_sogou,
                                    unlock_callback=unlock_callback,
                                    identify_image_callback=identify_image_callback,
                                    session=session)
        except WechatSogouException:
            return []
        gzh_list = WechatSogouStructuring.get_gzh_by_search(resp.text)
        for i in gzh_list:
            if decode_url:
                i['profile_url'] = self.__format_url(i['profile_url'], url, resp.text, unlock_callback=unlock_callback,
                                                     identify_image_callback=identify_image_callback, session=session)
            yield i

    def search_article(self, keyword, page=1, timesn=WechatSogouConst.search_article_time.anytime,
                       article_type=WechatSogouConst.search_article_type.all, ft=None, et=None,
                       unlock_callback=None,
                       identify_image_callback=None,
                       decode_url=True):
        """搜索 文章

        对于出现验证码的情况，可以由使用者自己提供：
            1、函数 unlock_callback ，这个函数 handle 出现验证码到解决的整个流程
            2、也可以 只提供函数 identify_image_callback，这个函数输入验证码二进制数据，输出验证码文字，剩下的由 wechatsogou 包来解决
        注意：
            函数 unlock_callback 和 identify_image_callback 只需要提供一个，如果都提供了，那么 identify_image_callback 不起作用

        Parameters
        ----------
        keyword : str or unicode
            搜索文字
        page : int, optional
            页数 the default is 1
        timesn : WechatSogouConst.search_article_time
            时间 anytime 没有限制 / day 一天 / week 一周 / month 一月 / year 一年 / specific 自定
            the default is anytime
        article_type : WechatSogouConst.search_article_type
            含有内容的类型 image 有图 / video 有视频 / rich 有图和视频 / all 啥都有
        ft, et : datetime.date or None
            当 tsn 是 specific 时，ft 代表开始时间，如： 2017-07-01
            当 tsn 是 specific 时，et 代表结束时间，如： 2017-07-15
        unlock_callback : callable
            处理出现验证码页面的函数，参见 unlock_callback_example
        identify_image_callback : callable
            处理验证码函数，输入验证码二进制数据，输出文字，参见 identify_image_callback_example
        decode_url : bool
            是否解析 url

        Returns
        -------
        list[dict]
            {
                'article': {
                    'title': '',  # 文章标题
                    'url': '',  # 文章链接
                    'imgs': '',  # 文章图片list
                    'abstract': '',  # 文章摘要
                    'time': ''  # 文章推送时间
                },
                'gzh': {
                    'profile_url': '',  # 公众号最近10条群发页链接
                    'headimage': '',  # 头像
                    'wechat_name': '',  # 名称
                    'isv': '',  # 是否加v
                }
            }

        Raises
        ------
        WechatSogouRequestsException
            requests error
        """
        url = WechatSogouRequest.gen_search_article_url(keyword, page, timesn, article_type, ft, et)
        print('search_article, url={}'.format(url))
        while True:
            session = self.__get_session()
            try:
                resp = self.__get_by_unlock(url,
                                            WechatSogouRequest.gen_search_article_url(keyword, article_type=article_type),
                                            unlock_platform=self.__unlock_sogou,
                                            unlock_callback=unlock_callback,
                                            identify_image_callback=identify_image_callback,
                                            session=session)
            except WechatSogouException as e:
                print(e)
                continue
            if self.need_login and not WechatSogouStructuring.is_login(resp.text):
                print('session not login, response text:{}'.format(resp.text))
                self.reset_session()
            else:
                break
        # print('response text:{}'.format(resp.text))
        article_list, has_next_page = WechatSogouStructuring.get_article_by_search(resp.text)
        print('has_next_page:{}'.format(has_next_page))
        for i in article_list:
            if decode_url:
                # print('article in result of search_article, before format, url={}, profile_url={}'.format(
                #     i['article']['url'], i['gzh']['profile_url']))
                i['article']['url'] = self.__format_url(i['article']['url'], url, resp.text,
                                                        unlock_callback=unlock_callback,
                                                        identify_image_callback=identify_image_callback,
                                                        session=session)
                i['gzh']['profile_url'] = self.__format_url(i['gzh']['profile_url'], url, resp.text,
                                                            unlock_callback=unlock_callback,
                                                            identify_image_callback=identify_image_callback,
                                                            session=session)
                # print('article in result of search_article, after format, url={}, profile_url={}'.format(
                #     i['article']['url'], i['gzh']['profile_url']))
            yield i, has_next_page

    def get_gzh_article_by_history(self, keyword=None, url=None,
                                   unlock_callback_sogou=None,
                                   identify_image_callback_sogou=None,
                                   unlock_callback_weixin=None,
                                   identify_image_callback_weixin=None):
        """从 公众号的最近10条群发页面 提取公众号信息 和 文章列表信息

        对于出现验证码的情况，可以由使用者自己提供：
            1、函数 unlock_callback ，这个函数 handle 出现验证码到解决的整个流程
            2、也可以 只提供函数 identify_image_callback，这个函数输入验证码二进制数据，输出验证码文字，剩下的由 wechatsogou 包来解决
        注意：
            函数 unlock_callback 和 identify_image_callback 只需要提供一个，如果都提供了，那么 identify_image_callback 不起作用

        Parameters
        ----------
        keyword : str or unicode
            公众号的id 或者name
        url : str or unicode
            群发页url，如果不提供url，就先去搜索一遍拿到url
        unlock_callback_sogou : callable
            处理出现 搜索 的时候出现验证码的函数，参见 unlock_callback_example
        identify_image_callback_sogou : callable
            处理 搜索 的时候处理验证码函数，输入验证码二进制数据，输出文字，参见 identify_image_callback_example
        unlock_callback_weixin : callable
            处理出现 历史页 的时候出现验证码的函数，参见 unlock_callback_example
        identify_image_callback_weixin : callable
            处理 历史页 的时候处理验证码函数，输入验证码二进制数据，输出文字，参见 identify_image_callback_example

        Returns
        -------
        dict
            {
                'gzh': {
                    'wechat_name': '',  # 名称
                    'wechat_id': '',  # 微信id
                    'introduction': '',  # 描述
                    'authentication': '',  # 认证
                    'headimage': ''  # 头像
                },
                'article': [
                    {
                        'send_id': '',  # 群发id，注意不唯一，因为同一次群发多个消息，而群发id一致
                        'datetime': '',  # 群发datatime
                        'type': '',  # 消息类型，均是49，表示图文
                        'main': 0,  # 是否是一次群发的第一次消息
                        'title': '',  # 文章标题
                        'abstract': '',  # 摘要
                        'fileid': '',  #
                        'content_url': '',  # 文章链接
                        'source_url': '',  # 阅读原文的链接
                        'cover': '',  # 封面图
                        'author': '',  # 作者
                        'copyright_stat': '',  # 文章类型，例如：原创啊
                    },
                    ...
                ]
            }


        Raises
        ------
        WechatSogouRequestsException
            requests error
        """
        if url is None:
            gzh_list = self.get_gzh_info(keyword, unlock_callback_sogou, identify_image_callback_sogou)
            if gzh_list is None:
                return {}
            if 'profile_url' not in gzh_list:
                raise Exception()  # todo use ws exception
            url = gzh_list['profile_url']

        resp = self.__get_by_unlock(url, WechatSogouRequest.gen_search_article_url(keyword),
                                    unlock_platform=self.__unlock_wechat,
                                    unlock_callback=unlock_callback_weixin,
                                    identify_image_callback=identify_image_callback_weixin)

        return WechatSogouStructuring.get_gzh_info_and_article_by_history(resp.text)

    def get_gzh_article_by_hot(self, hot_index, page=1, unlock_callback=None, identify_image_callback=None):
        """获取 首页热门文章

        Parameters
        ----------
        hot_index : WechatSogouConst.hot_index
            首页热门文章的分类（常量）：WechatSogouConst.hot_index.xxx
        page : int
            页数

        Returns
        -------
        list[dict]
            {
                'gzh': {
                    'headimage': str,  # 公众号头像
                    'wechat_name': str,  # 公众号名称
                },
                'article': {
                    'url': str,  # 文章临时链接
                    'title': str,  # 文章标题
                    'abstract': str,  # 文章摘要
                    'time': int,  # 推送时间，10位时间戳
                    'open_id': str,  # open id
                    'main_img': str  # 封面图片
                }
            }
        """

        assert hasattr(WechatSogouConst.hot_index, hot_index)
        assert isinstance(page, int) and page > 0

        url = WechatSogouRequest.gen_hot_url(hot_index, page)
        resp = self.__get_by_unlock(url,
                                    unlock_platform=self.__unlock_sogou,
                                    unlock_callback=unlock_callback,
                                    identify_image_callback=identify_image_callback)

        resp.encoding = 'utf-8'
        return WechatSogouStructuring.get_gzh_article_by_hot(resp.text)

    def get_article_content(self, url, del_qqmusic=True, del_mpvoice=True, unlock_callback=None,
                            identify_image_callback=None, hosting_callback=None, raw=False):
        """获取文章原文，避免临时链接失效

        Parameters
        ----------
        url : str or unicode
            原文链接，临时链接
        raw : bool
            True: 返回原始html
            False: 返回处理后的html
        del_qqmusic: bool
            True:微信原文中有插入的qq音乐，则删除
            False:微信源文中有插入的qq音乐，则保留
        del_mpvoice: bool
            True:微信原文中有插入的语音消息，则删除
            False:微信源文中有插入的语音消息，则保留
        unlock_callback : callable
            处理 文章明细 的时候出现验证码的函数，参见 unlock_callback_example
        identify_image_callback : callable
            处理 文章明细 的时候处理验证码函数，输入验证码二进制数据，输出文字，参见 identify_image_callback_example
        hosting_callback: callable
            将微信采集的文章托管到7牛或者阿里云回调函数，输入微信图片源地址，返回托管后地址

        Returns
        -------
        content_html
            原文内容
        content_img_list
            文章中图片列表

        Raises
        ------
        WechatSogouRequestsException
        """

        print('get_article_content, url={}'.format(url))
        try:
            resp = self.__get_by_unlock(url,
                                        unlock_platform=self.__unlock_wechat,
                                        unlock_callback=unlock_callback,
                                        identify_image_callback=identify_image_callback)
        except WechatSogouException as e:
            print(e)
            return None
        resp.encoding = 'utf-8'
        if '链接已过期' in resp.text:
            raise WechatSogouException('get_article_content 链接 [{}] 已过期'.format(url))
        if raw:
            return resp.text
        content_info = WechatSogouStructuring.get_article_detail(resp.text, del_qqmusic=del_qqmusic,
                                                                 del_voice=del_mpvoice)
        # print('get_article_content({}), content_info.img_list={}'.format(url, content_info[
        #     'content_img_list'] if content_info is not None else 'None'))
        if hosting_callback and content_info is not None:
            content_info = self.__hosting_wechat_img(content_info, hosting_callback)
        return content_info

    def get_sugg(self, keyword):
        """获取微信搜狗搜索关键词联想

        Parameters
        ----------
        keyword : str or unicode
            关键词

        Returns
        -------
        list[str]
            联想关键词列表

        Raises
        ------
        WechatSogouRequestsException
        """
        url = 'https://w.sugg.sogou.com/sugg/ajaj_json.jsp?key={}&type=wxpub&pr=web'.format(
            quote(keyword.encode('utf-8')))
        r = requests.get(url)
        if not r.ok:
            raise WechatSogouRequestsException('get_sugg', r)

        sugg = re.findall(u'\["' + keyword + '",(.*?),\["', r.text)[0]
        return json.loads(sugg)

    def get_gzh_detail(self, profile_url, wechat_name='', unlock_callback=None, identify_image_callback=None, decode_url=True):
        """根据公众号url（来源如文章列表）获取公众号详情

        对于出现验证码的情况，可以由使用者自己提供：
            1、函数 unlock_callback ，这个函数 handle 出现验证码到解决的整个流程
            2、也可以 只提供函数 identify_image_callback，这个函数输入验证码二进制数据，输出验证码文字，剩下的由 wechatsogou 包来解决
        注意：
            函数 unlock_callback 和 identify_image_callback 只需要提供一个，如果都提供了，那么 identify_image_callback 不起作用

        Parameters
        ----------
        profile_url : str
            URL
        wechat_name : str
            name of gzh
        unlock_callback : callable
            处理出现验证码页面的函数，参见 unlock_callback_example
        identify_image_callback : callable
            处理验证码函数，输入验证码二进制数据，输出文字，参见 identify_image_callback_example
        decode_url : bool
            是否解析 url

        Returns
        -------
        dict
        {
            'name': str, # 名称
            'avatar': str,  # 头像
            'wechat_id': str,  # 微信号
            'desc': str,  # 功能介绍
            'principal': str,  # 账号主体
            'qr_code': str,  # 二维码
        }

        Raises
        ------
        WechatSogouRequestsException
            requests error
        """

        session = self.__get_session()
        print('get_gzh_detail, profile_url={}'.format(profile_url))
        result = {}
        try:
            resp = self.__get_by_unlock(profile_url,
                                        unlock_platform=self.__unlock_wechat,
                                        unlock_callback=unlock_callback,
                                        identify_image_callback=identify_image_callback,
                                        session=session)
            result = WechatSogouStructuring.get_gzh_detail(resp.text)
        except WechatSogouException as e:
            print(e)
        if ('wechat_id' not in result or len(result['wechat_id']) == 0) and len(wechat_name) > 0:
            # get wechat_id by search_gzh
            name = wechat_name
            if 'name' in result and len(result['name']) > 0:
                name = result['name']
            gzhs = self.search_gzh(name)
            for gzh in gzhs:
                if gzh['wechat_name'] == name:
                    result['wechat_id'] = gzh['wechat_id']
                    result['name'] = gzh['wechat_name']
                    result['principal'] = gzh['authentication']
                    result['avatar'] = gzh['headimage']
                    result['desc'] = gzh['introduction']
                    break
        # if decode_url and result['qr_code'].startswith('/'):
        #     result['qr_code'] = 'https://mp.weixin.qq.com{}'.format(result['qr_code'])

        return result
