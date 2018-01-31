# coding=utf8

#
# 日志
#

import logging
from datetime import datetime
import os

from .util_config import BASE_DIR

LOG_PATH = os.path.join(BASE_DIR, 'log')

complicated_formatter = logging.Formatter(
    '%(asctime)s-%(name)s[%(levelname)s]:%(message)s')
simple_formatter = logging.Formatter('[%(levelname)s]<%(threadName)s>:%(message)s')


def get_logger(log_name, has_file=False, log_level=logging.DEBUG):
    now_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    logger = logging.getLogger(log_name)
    logger.setLevel(log_level)

    # 文件日志
    if has_file:
        # 创建log文件夹
        if not os.path.exists(LOG_PATH):
            os.mkdir(LOG_PATH)
        file_path = os.path.join(LOG_PATH, '{}-{}.log'.format(log_name, now_str))
        f_handler = logging.FileHandler(file_path)
        f_handler.setFormatter(complicated_formatter)
        logger.addHandler(f_handler)

    # 控制台打印
    c_handler = logging.StreamHandler()
    c_handler.setFormatter(simple_formatter)
    logger.addHandler(c_handler)

    return logger
