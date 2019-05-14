# -*-coding: utf-8 -*-
# author: yangkuii@outlook.com

import re
import logging
from conf import redis_conf, Logger
from tornado.web import RequestHandler
from database.model_orm import LinkControl
from database import RedisPool

redis = RedisPool()
hdl_log = Logger().get_logger('hdl', logging.INFO, ('file',))

import sys
reload(sys)
sys.setdefaultencoding('utf8')


def add_fix(name):
    return "%s_%s" % (redis_conf['key_prefix'], name)


class BaseHandler(RequestHandler):

    def prepare(self):
        self.session = self.application.session
        self.link_control = LinkControl(self.application.session)

    def on_finish(self):
        self.session.remove()


class ToshortenHandler(BaseHandler):

    def post(self):
        long_url = self.get_argument('long_url', default='', strip=True)
        if not long_url:
            hdl_log.info("ToshortenHandler: long_url=%s" % long_url)
            res = {'status':'failed', 'message':'long_url is required'}
            self.write(res)
            self.set_status(400, 'Parameter error')
        else:
            long_url = self.add_scheme(long_url.lower())
            link = self.link_control.exist_expand(long_url)
            if not link:
                link = self.link_control.add_url(long_url)
            res = {
                'status': 'success',
                'short_url': self.request.host+self.reverse_url("link_redirect", link.shorten)
            }

            # TODO 这里需要将 shorten long_url expires 形式存入redis。bc端用户极大几率在获取短链接十分钟内访问该链接
            # 在RedirectLinkHandler中先从redis中获取，如果没有再从数据库中获取

            redis.setex(add_fix(res['short_url']), long_url, 60*10)

            self.write(res)

    def add_scheme(self, url):
        """给 URL 添加 scheme(qq.com -> http://qq.com)"""
        # 支持的 URL scheme
        # 常规 URL scheme
        scheme2 = re.compile(r'(?i)^[a-z][a-z0-9+.\-]*://')
        # 特殊 URL scheme
        scheme3 = ('git@', 'mailto:', 'javascript:', 'about:', 'opera:',
                   'afp:', 'aim:', 'apt:', 'attachment:', 'bitcoin:',
                   'callto:', 'cid:', 'data:', 'dav:', 'dns:', 'fax:', 'feed:',
                   'gg:', 'go:', 'gtalk:', 'h323:', 'iax:', 'im:', 'itms:',
                   'jar:', 'magnet:', 'maps:', 'message:', 'mid:', 'msnim:',
                   'mvn:', 'news:', 'palm:', 'paparazzi:', 'platform:',
                   'pres:', 'proxy:', 'psyc:', 'query:', 'session:', 'sip:',
                   'sips:', 'skype:', 'sms:', 'spotify:', 'steam:', 'tel:',
                   'things:', 'urn:', 'uuid:', 'view-source:', 'ws:', 'xfire:',
                   'xmpp:', 'ymsgr:', 'doi:',
                   )
        url_lower = url.lower()

        # 如果不包含规定的 URL scheme，则给网址添加 http:// 前缀
        scheme = scheme2.match(url_lower)
        if not scheme:
            for scheme in scheme3:
                url_splits = url_lower.split(scheme)
                if len(url_splits) > 1:
                    break
            else:
                url = 'http://' + url
        return url


class TolongHandler(BaseHandler):

    def post(self):
        short_url = self.get_argument('short_url', default='', strip=True)

        if not short_url:
            res = {'status': 'failed', 'message': 'short_url is required'}
            self.set_status(400, 'Parameter error')
        else:
            link = self.link_control.get_expand(short_url)
            if not link:
                res = {
                    'status': 'failed',
                    'message': "not fount"
                }
                self.set_status(404, 'not found')
            else:
                res = {
                    'status': 'success',
                    'long_url': link.expand
                }
        self.write(res)


class RedirectLinkHandler(BaseHandler):

    def get(self, code):

        short_url = self.request.host + self.reverse_url("link_redirect", code)
        long_url = redis.get(add_fix(short_url))
        hdl_log.info("RedirectLinkHandler: long_url=%s" % long_url)
        if long_url:
            self.redirect(long_url)
            self.set_status(301)
        else:
            link = self.link_control.get_expand(code)
            if link:
                hdl_log.info("RedirectLinkHandler: long_url=%s" % link.expand)
                self.redirect(link.expand)
                self.set_status(301)
            else:
                res = {
                    'status': 'failed',
                    'message': "Links do not exist"
                }
                self.write(res)
                self.set_status(404, 'not found')
