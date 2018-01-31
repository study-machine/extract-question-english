# -*- coding: utf-8 -*-
# @Time    : 2018/1/16 下午3:55
# @Author  : wxy
# @File    : async_thread_runner.py
import threading

try:
    # py2
    from Queue import Queue, Empty
except:
    # py3
    from queue import Queue, Empty
import time

from ..logger_util import get_logger

log = get_logger('runner_log', has_file=False)


class AsyncRunner(object):
    def __init__(self, worker_num=3, time_out=30, log=log):
        self.WORKER_NUM = worker_num  # 子进程数量
        self.WORKER_TIMEOUT = time_out
        self.log = log
        self.WORKER_RUN = False
        self.workers = []
        self.queue = Queue(100)
        self.__start_workers()

    def __start_workers(self):
        """创建和启动线程"""
        for i in range(self.WORKER_NUM):
            worker = threading.Thread(target=self.__worker, name='worker%s' % (i + 1))
            self.workers.append(worker)

        self.WORKER_RUN = True
        for w in self.workers:
            w.start()

    def work_ok(self, info):
        pass

    def work_error(self, info):
        pass

    def __worker(self):
        """工作线程"""
        self.log.info('%s started' % threading.current_thread().name)
        thread_timeout = self.WORKER_TIMEOUT
        while True:
            try:
                # 从队列获取方法和数据
                fn, data = self.queue.get(timeout=2)
                self.log.debug('{} start work fn:{}'.format(threading.current_thread().name, fn.__name__))
                # 根据数据类型解包
                if isinstance(data, tuple):
                    fn(*data)
                elif isinstance(data, dict):
                    fn(**data)
                else:
                    fn()
                self.log.debug('{} finish work fn:{}'.format(threading.current_thread().name, fn.__name__))
            except Empty:
                thread_timeout -= 1
                if not self.WORKER_RUN:
                    self.work_ok('ok:%s' % threading.current_thread().name)
                    self.log.info('worker %s 正常结束' % threading.current_thread().name)
                    break
                elif thread_timeout <= 0:
                    self.work_error('worker %s 线程超时退出' % threading.current_thread().name)
                    self.log.info('worker %s 线程超时退出' % threading.current_thread().name)
                    break
                continue
            except Exception as e:
                # 其他异常退出
                self.work_error('exception form get queue:%s' % e)
                self.log.critical('exception form get queue:%s' % e)
                self.log.info('worker %s  finally ended' % threading.current_thread().name)
                raise

    def put_queue(self, fn, *args, **kwargs):
        # 根据参数类型解包，将方法和数据放入队列
        if args:
            self.queue.put((fn, args))
        elif kwargs:
            self.queue.put((fn, kwargs))
        else:
            # 无参数的情况
            self.queue.put((fn, None))
        self.log.debug('worker_queue put work,qsize:%s' % self.queue.qsize())

    def finish_workers(self):
        # 结束worker和等待结束
        self.WORKER_RUN = False
        self.log.info('stop_workers')
        self.log.info('finish_workers')
        for w in self.workers:
            w.join()
