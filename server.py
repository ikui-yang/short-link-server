# -*-coding: utf-8 -*-
# author: yangkuii@outlook.com

import os
import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.options import define, options
from sqlalchemy.orm import sessionmaker, scoped_session
from database import RedisPool, engine
from router import router_list


define("port", default=5001, help="run on the given port", type=int)

if __name__ == '__main__':
    tornado.options.parse_command_line()

    handlers = router_list
    if os.environ['environment'] == 'prod':
        settings = {
            "debug": True
        }
    else:
        settings = {
            "debug": False
        }


    class Application(tornado.web.Application):
        def __init__(self):
            tornado.web.Application.__init__(self, handlers, **settings)
            self.session = scoped_session(sessionmaker(bind=engine))


    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


