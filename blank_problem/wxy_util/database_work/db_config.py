# -*- coding: utf-8 -*-
# @Time    : 2017/12/22 下午12:21
# @Author  : wxy
# @File    : db_config.py

import sys

VERSION = sys.version


class DatabaseConfig(object):
    """
    local:      myself db
    play:       玩库
    dev:        dev db      api开发库
    test:       qa db       qa测试库
    online:     online db
    read_only:  online_slave_db
    """

    class Tiku(object):
        db_type = 'mysql'
        config = {
            'local': {
                'host': 'test.wangxiyang.com',
                'user': 'root',
                'port': 3306,
                'password': 'asd123',
                'db': 'tiku_empty',
                'charset': 'utf8mb4',
                'use_unicode': False if VERSION == '2' else True,
            },
            'play': {
                'host': '10.10.48.120',
                'user': 'lyj',
                'port': 3308,
                'password': 'lyj123',
                'db': 'tiku_empty',
                'charset': 'utf8mb4',
                'use_unicode': False if VERSION == '2' else True
            },
            'dev': {
                'host': '10.10.228.163',
                'user': 'test',
                'port': 3301,
                'password': 'OnlyKf!@#',
                'db': 'tiku',
                'charset': 'utf8mb4',
                'use_unicode': False if VERSION == '2' else True,
            },
            'test': {
                'host': '10.9.35.226',
                'user': 'test',
                'port': 3329,
                'password': 'qaOnly!@#',
                'db': 'tiku',
                'charset': 'utf8mb4',
                'use_unicode': False if VERSION == '2' else True,
            },
            'read_only': {
                'host': '10.215.50.122',
                'user': 'wangxy',
                'port': 3306,
                'password': 'wangxy112',
                'db': 'tiku',
                'charset': 'utf8mb4',
                'use_unicode': False if VERSION == '2' else True
            }

        }

    class KnowBoxStore(object):
        db_type = 'mysql'
        config = {
            'local': {
                'host': 'test.wangxiyang.com',
                'user': 'root',
                'port': 3306,
                'password': 'asd123',
                'db': 'knowboxstore_new',
                'charset': 'utf8mb4',
                'use_unicode': False if VERSION == '2' else True
            },
            'test': {
                'host': '10.9.35.226',
                'user': 'test',
                'port': 3339,
                'password': '123456',
                'db': 'knowboxstore_susuan',
                'charset': 'utf8mb4',
                'use_unicode': False if VERSION == '2' else True
            },
            'read_only': {
                'host': '10.9.198.64',
                'user': 'wangxy',
                'port': 3306,
                'password': 'wangxy112',
                'db': 'knowboxstore',
                'charset': 'utf8mb4',
                'use_unicode': False if VERSION == '2' else True
            },
            'online': {
                'host': '10.19.141.31',
                'user': 'wangxy',
                'port': 3306,
                'password': 'wangxy112',
                'db': 'knowboxstore',
                'charset': 'utf8mb4',
                'use_unicode': False if VERSION == '2' else True
            }

        }
        config['dev'] = config['test']
        config['play'] = config['test']

    class Medivh(object):
        db_type = 'mysql'
        config = {
            'local': {
                'host': 'test.wangxiyang.com',
                'user': 'root',
                'port': 3306,
                'password': 'asd123',
                'db': 'medivh_dev',
                'charset': 'utf8mb4',
                'use_unicode': False if VERSION == '2' else True
            },
            'test': {
                'host': '10.9.41.75',
                'user': 'cache',
                'port': 3308,
                'password': 'cache_all',
                'db': 'ss_medivch',
                'charset': 'utf8mb4',
                'use_unicode': False if VERSION == '2' else True
            }
        }
        config['dev'] = config['test']
        config['online'] = config['test']

    class ExcelStore(object):
        db_type = 'mysql'
        config = {
            'local': {
                'host': 'test.wangxiyang.com',
                'user': 'root',
                'port': 3306,
                'password': 'asd123',
                'db': 'excel_store',
                'charset': 'utf8mb4',
                'use_unicode': False if VERSION == '2' else True,

            }
        }
        config['dev'] = config['local']
        config['test'] = config['local']
        config['online'] = config['local']

    class MyTest(object):
        db_type = 'mysql'
        config = {
            'local': {
                'host': 'test.wangxiyang.com',
                'user': 'root',
                'port': 3306,
                'password': 'asd123',
                'db': 'mytest',
                'charset': 'utf8mb4',
                'use_unicode': False if VERSION == '2' else True
            }
        }

    class TmpDB(object):
        db_type = 'mysql'

        config = {
            'local': {
                'host': 'test.wangxiyang.com',
                'user': 'root',
                'port': 3306,
                'password': 'asd123',
                'db': 'knowboxstore5',
                'charset': 'utf8mb4',
                'use_unicode': False if VERSION == '2' else True
            },
            'dev': {
                'host': '10.10.48.120',
                'user': 'lyj',
                'port': 3308,
                'password': 'lyj123',
                'db': 'knowboxstore_wxy',
                'charset': 'utf8mb4',
                'use_unicode': False if VERSION == '2' else True,

            }
        }
