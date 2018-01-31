# -*- coding: utf-8 -*-
# @Time    : 2018/1/8 下午9:15
# @Author  : wxy
# @File    : others.py
from itertools import groupby

import os


def group_by_key(data, key):
    """
    字典列表分组
    :param data:    dict_list   数据列表
    :param key:     str         键名
    :return:        dict_list   [{'key': 'key_name','data':[...]},...]
    """

    def key_fn(x): return x[key]

    gl = groupby(sorted(data, key=key_fn), key_fn)
    return [{'key': t[0], 'data': list(t[1])} for t in gl]


def get_upper_dir(abs_path, n):
    """获取上n级的路径"""
    if n == 0:
        return abs_path
    path = os.path.dirname(abs_path)
    return get_upper_dir(path, n - 1)
