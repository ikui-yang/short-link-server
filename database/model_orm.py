# -*-coding: utf-8 -*-
# author: yangkuii@outlook.com

from random import randint
from .models import Link, IncrNum
from diyidan_link_server.libs.short_url import UrlEncoder
from sqlalchemy.orm.exc import NoResultFound


import sys
reload(sys)
sys.setdefaultencoding('utf8')

# Session = sessionmaker(bind=engine)


class LinkControl(object):

    def __init__(self, session):
        self.session = session

    def exist_expand(self, long_url):
        link = self.session.query(Link.shorten, Link.expand).filter_by(expand=long_url).one_or_none()
        return link

    def add_url(self, long_url):
        id = IncrNumControl(self.session).get_id('link')
        short_url = UrlEncoder()
        link_obj = Link(
                shorten=short_url.encode_url(int(id) * 1000 + randint(100, 999)),
                expand=long_url
            )
        # 使用try语句主要是为了在插入成功的情况下拿到插入对象，减轻数据库压力
        try:
            self.session.add(link_obj)
            self.session.commit()
            # raise Exception("Don't worry, just to test code stability", )
        except Exception as e:
            self.session.rollback()
            raise e
        return link_obj

    def get_expand(self, short_url):
        link = self.session.query(Link.shorten, Link.expand).filter_by(shorten=short_url.split(r'/')[-1]).one_or_none()
        return link




class IncrNumControl(object):

    def __init__(self, session):
        self.session = session

    # 获取自增ID
    def get_id(self, name):

        try:
            incr_num = self.session.query(IncrNum).filter_by(name=name).one()
        except NoResultFound as e:
            incr_num = IncrNum(name=name, value=0)
            self.session.add(incr_num)
        incr_num.value = incr_num.value + 1
        try:
            self.session.commit()
        except:
            self.session.rollback()

        return incr_num.value
