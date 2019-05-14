# -*-coding: utf-8 -*-
# author: yangkuii@outlook.com

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BigInteger, String, Text, DateTime, Integer, func

import sys
reload(sys)
sys.setdefaultencoding('utf8')


Base = declarative_base()

class BaseModel(Base):
    """继承类"""
    __abstract__ = True
    _table_args__ = {'mysql_charset': 'utf8', 'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='修改时间')


class Link(BaseModel):

    __tablename__ = 'links'
    shorten = Column(String(80), nullable=False, unique=True, comment='短链接', index=True)
    expand = Column(Text(255), nullable=False, comment='长链接')


class IncrNum(BaseModel):

    __tablename__ = 'incrnums'

    name = Column(String(8), nullable=False, unique=True, comment="计数名称")
    value = Column(BigInteger, nullable=False, comment="计数值")




if __name__ == '__main__':
    from diyidan_link_server.database import engine
    Base.metadata.create_all(engine)
