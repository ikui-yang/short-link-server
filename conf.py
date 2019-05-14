# -*-coding: utf-8 -*-
# author: yangkuii@outlook.com

import os
import logging

if os.environ['environment'] == 'local':
    mysql_conf = {
        'host': '127.0.0.1',
        'user': 'root',
        'passwd': 'root',
        'db': 'diyidan_link_service',
        'port': '3306',
        'charset': 'utf8mb4',

    }
    redis_conf = {
        'host': '127.0.0.1',
        'passwd': '',
        'db': '0',
        'port': '6379',
        'key_prefix': 'diyidan_link_service'
    }
    # orm_logger = logging.getLogger('orm')
    # orm_logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler('/opt/log.txt')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # orm_logger.addHandler(console_handler)
    # orm_logger.addHandler(file_handler)



elif os.environ['environment'] == 'dev':
    pass

else:
    pass


class Logger(object):

    logger_dict = {}

    @classmethod
    def add_logger(cls, name, level, output_type):
        """创建一个logger对象"""
        obj = logging.getLogger(name)
        obj.setLevel(level)
        out_put_dict = {
            'console': console_handler,
            'file': file_handler
        }
        for _t in output_type:
            obj.addHandler(out_put_dict[_t])

        cls.logger_dict[name] = obj
        return obj

    @classmethod
    def get_logger(cls, name, level, output_type):
        """获取logger对象，没有则创建"""
        if name in cls.logger_dict:
            return cls.logger_dict[name]
        else:
            return cls.add_logger(name, level, output_type)



