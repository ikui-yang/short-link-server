# -*-coding: utf-8 -*-
# author: yangkuii@outlook.com

from tornado.web import url
from handlers import ToshortenHandler, TolongHandler, RedirectLinkHandler

router_list = [
    url(r'/link/shorten', ToshortenHandler, name='get_short'),
    url(r'/link/expend', TolongHandler, name='get_lang'),
    url(r'/(\w*)', RedirectLinkHandler, name='link_redirect')
]
