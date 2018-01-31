# -*- coding: utf-8 -*-
# @Time    : 2017/12/4 下午9:51
# @Author  : wxy
# @File    : async_db.py

from .async_thread_runner import AsyncRunner
from .db_rw import DatabaseRW
from ..logger_util import get_logger

async_writer_log = get_logger('async_writer_log', has_file=False)


class BaseAsyncDBWriter(DatabaseRW, AsyncRunner):
    """异步写库工作类"""

    def __init__(self, env, work_num=3, time_out=30, log=async_writer_log):
        """
        :param db_config:   连接设置
        :param work_num:    子进程数量
        """
        DatabaseRW.__init__(self, env)
        AsyncRunner.__init__(self, work_num, time_out, log)
        self.log = log

    def async_batch_insert_or_update_data(self, *args, **kwargs):
        """异步批量插入或更新唯一"""
        self.put_queue(self.batch_insert_or_update_data, *args, **kwargs)

    def async_batch_update_data(self, *args, **kwargs):
        """异步批量更新数据"""
        if args:
            self.queue.put((self.batch_update_data, args))
        elif kwargs:
            self.queue.put((self.batch_update_data, kwargs))
        self.log.debug('write_queue has put data,qsize:%s' % self.queue.qsize())

    def work_ok(self, info):
        self.log.info(info + ' 执行commit')
        self.commit()

    def work_error(self, info):
        self.log.info(info + ' 执行rollback')
        self.rollback()
