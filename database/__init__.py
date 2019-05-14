# -*-coding: utf-8 -*-
# author: yangkuii@outlook.com

import redis
import threading
from diyidan_link_server.conf import mysql_conf, redis_conf
from sqlalchemy import create_engine

import sys
reload(sys)
sys.setdefaultencoding('utf8')



engine = create_engine(
    'mysql+pymysql://%(user)s:%(passwd)s@%(host)s:%(port)s/%(db)s?charset=%(charset)s' % mysql_conf,
    echo=True,
    max_overflow=0,  # 超过连接池大小外最多创建的连接
    pool_size=5,  # 连接池大小
    pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
    pool_recycle=-1  # 多久之后对线程池中的线程进行一次连接的回收（重置）
)


class RedisPool(object):
    __mutex = threading.Lock()
    __remote = {}
    host = redis_conf['host']
    passwd = redis_conf['passwd']
    db = redis_conf['db']
    port = redis_conf['port']

    def __new__(cls):
        with RedisPool.__mutex:
            redis_key = "%s:%s:%s" % (cls.host, cls.port, cls.db)
            redis_obj = RedisPool.__remote.get(redis_key)

            if redis_obj is None:
                redis_obj = RedisPool.__remote[redis_key] = RedisPool.new_redis_pool(cls.host, cls.passwd, cls.port, cls.db)
        return redis.Redis(connection_pool=redis_obj)

    @staticmethod
    def new_redis_pool(host, passwd, port, db):
        redis_obj = redis.ConnectionPool(host=host, password=passwd,port=port, db=db, socket_timeout=3, max_connections=30)
        return redis_obj
