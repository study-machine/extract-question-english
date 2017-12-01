# -*- coding: utf-8 -*-
# @Time    : 2017/11/30 下午9:20
# @Author  : wxy
# @File    : db.py

class DatabaseConfig(object):
    local_db = {
        'host': 'test.wangxiyang.com',
        'user': 'root',
        'port': 3306,
        'password': 'asd123',
        'db': 'tiku-dev',
        'charset': 'utf8mb4',
        'use_unicode': False,
    }

    dev_db = {
        'host': '10.10.228.163',
        'user': 'test',
        'port': 3301,
        'password': 'OnlyKf!@#',
        'db': 'tiku',
        'charset': 'utf8mb4',
        'use_unicode': False,
    }
