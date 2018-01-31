# -*- coding: utf-8 -*-
# @Time    : 2018/1/31 下午6:13
# @Author  : wxy
# @File    : run.py
import re
import json
from wxy_util.database_work import DatabaseRW, DatabaseConfig


class Store(DatabaseRW):
    db_config = DatabaseConfig.KnowBoxStore
    read_only = True

    def ques_en_20(self):
        sql = """
        select question_id,right_answer from base_question
        where show_type=20 and subject=2
        and status=0 and online_status=2
        """
        return self.select_fetchall(sql)


def check_blank(env):
    store = Store('local')
    for row in store.ques_en_20():
        jd = json.loads(row['right_answer'])
        content = jd[0]['content']
        if ' ' in content:
            print row


if __name__ == '__main__':
    check_blank('online')
