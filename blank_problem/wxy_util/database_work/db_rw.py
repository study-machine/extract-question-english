# -*- coding: utf-8 -*-
# @Time    : 2018/1/16 下午3:57
# @Author  : wxy
# @File    : db_rw.py
import threading
import traceback

import pymysql

"""
Py2 Py3 通用
"""


class _LazyConnection(object):
    """惰性连接"""

    def __init__(self, db_config, cursor_class=pymysql.cursors.DictCursor):
        self.db_config = db_config
        self.cursor_class = cursor_class
        self.conn = None

    def __get_conn(self):
        if not self.conn:
            self.conn = self.conn = pymysql.connect(
                cursorclass=pymysql.cursors.DictCursor, **self.db_config)
            print('%s 建立连接:%s' % (threading.current_thread().name, self.db_config['db']))
        return self.conn

    @property
    def cursor(self):
        return self.__get_conn().cursor()

    def commit(self):
        if not self.conn:
            print('没有建立连接,commit失败')
            return
        self.conn.commit()

    def rollback(self):
        if not self.conn:
            print('没有连接,无法回滚')
            return
        self.conn.rollback()

    def __del__(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            print('%s 连接关闭' % threading.current_thread().name)


class DBCtx(threading.local):
    """线程隔离连接环境"""

    def __init__(self, db_config, cursor_class=pymysql.cursors.DictCursor):
        self.conn = _LazyConnection(db_config, cursor_class)

    @property
    def cursor(self):
        return self.conn.cursor

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()


class DatabaseRW(object):
    """普通读写库工作类"""
    db_config = None  # 数据库配置
    read_only = False  # 设置只读数据库（从库）

    def __init__(self, env='local'):
        """
        env 为db_config中的连接配置,如果类属性read_only为True时，无视env直接使用read_only
        local:      myself
        dev:        dev db
        test:       qa db
        online:     online db
        read_only:  online_slave_db
        """
        if self.read_only and env != 'local':
            db_config = self.db_config.config['read_only']
        else:
            db_config = self.db_config.config[env]
        self.db_ctx = DBCtx(db_config)

    def commit(self):
        self.db_ctx.commit()

    def rollback(self):
        self.db_ctx.rollback()

    @staticmethod
    def add_back_quote(column_names):
        """给字段名添加反引号"""
        return ['`%s`' % name for name in column_names]

    @staticmethod
    def trans_insert_or_replace_sql(table_name, column_names, replace=False):
        """
        转换INSERT SQL语句
        :param table_name:      表名
        :param column_names:    插入字段名
        :param replace:         是否使用replace
        :return:                SQL语句
        """
        column_names = DatabaseRW.add_back_quote(column_names)
        colunm_string = ','.join(column_names)
        s_string = '{}'.format(','.join(['%s' for _ in range(len(column_names))]))
        method_str = 'INSERT'
        if replace:
            method_str = 'REPLACE'
        sql = """
        {} INTO {} ({}) VALUES ({})
        """.format(method_str, table_name, colunm_string, s_string)
        return sql

    @staticmethod
    def trans_duplicate_update_sql(d_updates_names):
        """唯一键更新字段名sql拼接"""
        tmp = []
        for name in d_updates_names:
            tmp.append('%s=VALUES(%s)' % (name, name))
        return 'ON DUPLICATE KEY UPDATE ' + ','.join(tmp)

    @staticmethod
    def trans_update_sql(table_name, set_column_names, where_column_names):
        """更新sql拼接"""
        set_str_list = []
        for name in set_column_names:
            set_str_list.append('{}=%s'.format(name))
        set_str = ','.join(set_str_list)

        where_str_list = []
        for name in where_column_names:
            where_str_list.append('{}=%s'.format(name))
        where_str = ' AND '.join(where_str_list)
        sql = """
        UPDATE {table_name} SET {set_str}
        WHERE {where_str}
        """.format(table_name=table_name, set_str=set_str, where_str=where_str)
        return sql

    def execute(self, sql, value_params=None, is_many=False):
        with self.db_ctx.cursor as cursor:
            try:
                if is_many:
                    cursor.executemany(sql, value_params)
                else:
                    cursor.execute(sql, value_params)
            except Exception:
                raise Exception(traceback.format_exc(), sql, value_params)

    def single_insert_for_id(self, table_name, column_names, value_params):
        """
        单条插入返回自增ID
        :param table_name:      str 表名
        :param column_names:    list 插入字段名
        :param value_params:    tuple 插入值，需要和字段对应
        :return:                新增ID
        """
        sql = self.trans_insert_or_replace_sql(table_name, column_names)
        with self.db_ctx.cursor as cursor:
            cursor.execute(sql, value_params)
            new_id = cursor.lastrowid
            return new_id

    def single_insert_or_update(self, table_name, column_names, value_params, d_updates_names=None):
        """
        单条插入或加唯一更新
        :param table_name: str 表名
        :param column_names: list 插入字段名
        :param value_params: tuple 插入值，需要和字段对应
        :param d_updates_names: list 可选，唯一更新字段名，None就是普通插入
        :return: 返回自增ID
        """
        sql = self.trans_insert_or_replace_sql(table_name, column_names)
        if d_updates_names:
            sql += self.trans_duplicate_update_sql(d_updates_names)
        self.execute(sql, value_params, False)

    def batch_insert_or_update_data(self, table_name, column_names, value_params, d_updates_names=None):
        """
        批量插入或加唯一更新数据
        :param table_name: str 表名
        :param column_names: list 插入字段名
        :param value_params: tuple_list 插入值列表，需要和字段对应
        :param d_updates_names: list 可选，唯一更新字段名，None就是普通插入
        :return:
        """
        sql = self.trans_insert_or_replace_sql(table_name, column_names)
        if d_updates_names:
            sql += self.trans_duplicate_update_sql(d_updates_names)
        self.execute(sql, value_params, True)

    def batch_replace_data(self, table_name, column_names, value_params):
        """
        批量插入或替换唯一冲突数据
        :param table_name: str 表名
        :param column_names: list 插入字段名
        :param value_params: tuple_list 插入值列表，需要和字段对应
        :return:
        """
        sql = self.trans_insert_or_replace_sql(table_name, column_names, True)
        self.execute(sql, value_params, True)

    def single_update_data(self, table_name, set_column_names, where_column_names, value_params):
        """
        单次执行更新数据
        :param table_name:          string  表名
        :param set_column_names:    list    更新字段名
        :param where_column_names:  list    限制字段名（现只支持=操作）
        :param value_params:        tuple   (更新数据..，限制数据..) 只有 where=
        :return:
        """
        sql = self.trans_update_sql(table_name, set_column_names, where_column_names)
        self.execute(sql, value_params, False)

    def batch_update_data(self, table_name, set_column_names, where_column_names, value_params):
        """
        批量执行更新数据
        :param table_name:          string  表名
        :param set_column_names:    list    更新字段名
        :param where_column_names:  list    限制字段名（现只支持=操作）
        :param value_params:        list    数据tuple_list，[(更新数据..，限制数据..),...] (where=限制数据)
        :return:
        """
        sql = self.trans_update_sql(table_name, set_column_names, where_column_names)
        self.execute(sql, value_params, True)

    def select_fetchall(self, sql, single_value=''):
        """
        获取 select 结果列表
        :param sql:             sql语句
        :param single_value:    只返回单个字段的列表,如：question_id
        :return:                结果的dict列表，或value列表
        """
        with self.db_ctx.cursor as cursor:
            try:
                cursor.execute(sql)
            except Exception:
                raise Exception(traceback.format_exc(), sql)
            result_list = cursor.fetchall()
        if not result_list:
            return []
        if single_value:
            return [x[single_value] for x in result_list]
        else:
            return result_list

    def huge_table_generator(self, table_name, range_count, column_names=None):
        """
        表记录生成器，单个表查询用这个
        :param table_name:      str         表名
        :param range_count:     int         每次迭代记录数
        :param column_names:    str list    字段名列表
        :return:    数据记录生成器
        """
        sql = 'select count(*) as count from %s' % table_name
        row_count = self.select_fetchall(sql)[0]['count']
        if not row_count:
            raise Exception('table:%s,没有数据')
        if column_names:
            column_names_str = ','.join(column_names)
        else:
            column_names_str = '*'
        return self.huge_query_generator(
            sql='select %s from %s' % (column_names_str, table_name),
            row_count=row_count,
            range_count=range_count,
        )

    def huge_query_generator(self, sql, row_count, range_count):
        """
        大量查询记录迭代器，复杂sql用这个
        :param sql:             str     sql语句
        :param row_count:       int     总记录数
        :param range_count:     int     每次迭代记录数
        :return:    数据记录生成器
        """
        for i in range(0, row_count, range_count):
            new_sql = sql + ' limit %s,%s' % (i, range_count)
            yield self.select_fetchall(new_sql)
