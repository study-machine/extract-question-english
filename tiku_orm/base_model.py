# coding=utf-8
import pymysql
from copy import deepcopy

from base_field import BaseField
from tiku_orm.config import db_config_read, db_config_write


class ModelMetaClass(type):
    def __new__(cls, name, bases, attrs):
        # 拷贝字段属性
        column_names = []
        for k, v in attrs.items():
            if isinstance(v, BaseField):
                attrs[k] = deepcopy(v)
                column_names.append(k)
        cls = type.__new__(cls, name, bases, attrs)
        return cls


class BaseModel(object):
    __metaclass__ = ModelMetaClass
    # 读库的连接
    conn_read = pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **db_config_read)
    # 写库的连接
    conn_write = pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **db_config_write)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return '<id:{},name:{}>'.format(self.id, self.name)

    @classmethod
    def get_read_cursor(cls):
        return cls.conn_read.cursor()

    @classmethod
    def get_write_cursor(cls):
        return cls.conn_write.cursor()

    @classmethod
    def select(cls, sql):
        cursor = cls.get_read_cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    @classmethod
    def insert(cls, sql, auto_commit=True):
        cursor = cls.get_write_cursor()
        cursor.execute(sql)
        if auto_commit:
            cls.commit()
        return cursor.lastrowid

    @classmethod
    def commit(cls):
        cls.conn_write.commit()

    def insert_new_row(self):
        if not getattr(self, 'insert_dict', None) or not getattr(self, '__tablename__', None):
            raise Exception('没有插入字段名或表名')
        column_values = []
        column_names = []
        for k, v in self.insert_dict.items():
            column_values.append(getattr(self, k))
            column_names.append(v)
        column_values_str = map(lambda v: '\"{}\"'.format(str(v)), column_values)

        sql = """INSERT INTO {} ({}) VALUES({});
        """.format(self.__tablename__, ','.join(column_names), ','.join(column_values_str))
        try:
            self.id = self.insert(sql)
        except Exception, e:
            raise Exception, e
