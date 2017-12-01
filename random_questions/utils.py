# coding=utf8
from datetime import datetime
from random import randint


def get_datetime_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def fix_six_times(c_qs, b_qs):
    """不足6的倍数，备选题补全"""
    n = len(c_qs) % 6
    if n != 0:
        if len(b_qs) < 6 - n:
            # 被选题数量并不足以补全
            c_qs = c_qs[:n * 6]
            return
        for i in xrange(6 - n):
            # 随机从备选题中补足6的倍数
            q = pop_random_question(b_qs)
            if q:
                c_qs.append(q)


def pop_random_question_by_type(qs, q_type):
    """根据类型pop随机题目"""
    type_qs = [q for q in qs if q.q_type == q_type]
    return pop_random_question(type_qs)


def pop_random_question(qs):
    """选随机题目"""
    if qs:
        return qs.pop(randint(0, len(qs) - 1))


def sort_question_by_group(question_list):
    """题有排序需求，按照音,形,义的顺序排列"""
    sort_value = {
        '音': 1,
        '形': 2,
        '义': 3,
    }
    return sorted(question_list, key=lambda q: sort_value.get(q.q_type, 4))


QUESTION_TYPE = {
    7924: '中英互译',
    7925: '图文互译',
    7926: '单词拼写',
    7927: '组合单词',
    7928: '听句选词',
    7929: '选词填空',
    7930: '听音排序',
    7931: '连词成句',
    7932: '补全单词',
}
