# coding=utf-8
class BaseField(object):
    data = None

    def __init__(self, column_name=''):
        self.column_name = column_name

    def __get__(self, instance, owner):
        return self.data


class StringField(BaseField):
    """字符串字段"""

    def __set__(self, instance, value):
        if isinstance(value, unicode):
            self.data = value.encode('utf8')
        self.data = value


class IntegerField(BaseField):
    """整数字段"""

    def __set__(self, instance, value):
        self.data = int(value)