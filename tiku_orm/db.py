# -*- coding: utf-8 -*-
# @Time    : 2017/12/8 下午4:20
# @Author  : wxy
# @File    : db.py

# coding=utf8
class DatabaseConfig(object):
    excel_store = {
        'host': 'test.wangxiyang.com',
        'user': 'root',
        'port': 3306,
        'password': 'asd123',
        'db': 'excel_store',
        'charset': 'utf8mb4',
        'use_unicode': False,
    }

    local_tiku_db = {
        'host': 'test.wangxiyang.com',
        'user': 'root',
        'port': 3306,
        'password': 'asd123',
        'db': 'tiku-dev',
        'charset': 'utf8mb4',
        'use_unicode': False,
    }

    dev_tiku_db = {
        'host': '10.10.228.163',
        'user': 'test',
        'port': 3301,
        'password': 'OnlyKf!@#',
        'db': 'tiku',
        'charset': 'utf8mb4',
        'use_unicode': False,
    }

    qa_tiku_db = {
        'host': '10.9.35.226',
        'user': 'test',
        'port': 3329,
        'password': 'qaOnly!@#',
        'db': 'tiku',
        'charset': 'utf8mb4',
        'use_unicode': False,
    }

    local_knowboxstore_db = {
        'host': 'test.wangxiyang.com',
        'user': 'root',
        'port': 3306,
        'password': 'asd123',
        'db': 'knowboxstore5',
        'charset': 'utf8mb4',
        'use_unicode': False
    }

    dev_knowboxstore_db = {
        'host': '10.10.48.120',
        'user': 'lyj',
        'port': 3308,
        'password': 'lyj123',
        'db': 'knowboxstore_wxy',
        'charset': 'utf8mb4',
        'use_unicode': False
    }

    qa_knowboxstore_db = {
        'host': '10.9.35.226',
        'user': 'test',
        'port': 3339,
        'password': '123456',
        'db': 'knowboxstore_susuan',
        'charset': 'utf8mb4',
        'use_unicode': False
    }

    online_knowboxstore_db = {
        'host': '10.19.141.31',
        'user': 'wangxy',
        'port': 3306,
        'password': 'wangxy112',
        'db': 'knowboxstore',
        'charset': 'utf8mb4',
        'use_unicode': False
    }

    # 线上题库从库
    online_slave_db = {
        'host': '10.215.48.111',
        'user': 'liyj',
        'port': 3306,
        'password': 'liyj123',
        'db': 'tiku',
        'charset': 'utf8mb4',
        'use_unicode': False
    }

    local_test_db = {
        'host': 'test.wangxiyang.com',
        'user': 'root',
        'port': 3306,
        'password': 'asd123',
        'db': 'mytest',
        'charset': 'utf8mb4',
        'use_unicode': False
    }
