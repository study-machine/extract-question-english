# coding=utf8

#
# 日志
#

import logging
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath((os.path.dirname(__file__))))
LOG_PATH = os.path.join(BASE_DIR, 'log')
if not os.path.exists(LOG_PATH):
    os.mkdir(LOG_PATH)

complicated_formatter = logging.Formatter('%(asctime)s-%(name)s[%(levelname)s]:%(message)s')
simple_formatter = logging.Formatter('[%(levelname)s]:%(message)s')


def get_logger(log_name):
    now_str = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    file_path = os.path.join(LOG_PATH, '{}-{}.log'.format(log_name, now_str))
    f_handler = logging.FileHandler(file_path)
    f_handler.setLevel(logging.DEBUG)
    f_handler.setFormatter(complicated_formatter)

    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG)
    c_handler.setFormatter(simple_formatter)

    logger = logging.getLogger(log_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(f_handler)
    logger.addHandler(c_handler)

    return logger
