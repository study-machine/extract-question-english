# coding=utf8
from tiku_orm.base_field import *
from tiku_orm.base_model import *
from random_questions.utils import *


#
# 题库总库knowboxstore模型
#


class SectionBaseStore(BaseModel):
    __tablename__ = 'base_course_section'
    insert_dict = {
        'name': 'name',
        'summary': 'summary',
        'level': 'level',
        'parent_id': 'parent_id',
        'order_num': 'order_num',
        'section_order': 'section_order',
        'assist_id': 'assist_id',
        'last': 'last',
        'q_type': 'question_type',
    }

    def __init__(self, **kwargs):

        self.id = IntegerField(column_name='section_id')  # SectionID
        self.name = StringField(column_name='name')  # SectionName
        self.summary = StringField(column_name='summary')
        self.level = IntegerField(column_name='level')  # level
        self.parent_id = IntegerField(column_name='parent_id')
        self.order_num = IntegerField(column_name='order_num')  # 顺序
        self.section_order = IntegerField(column_name='section_order')  # 综合顺序
        self.assist_id = IntegerField(column_name='assist_id')  # 教辅id
        self.last = IntegerField(column_name='last')
        self.q_type = IntegerField(column_name='question_type')  # 章节type21
        self.online_status = 1
        self.status = 0
        super(SectionBaseStore, self).__init__(**kwargs)

        self.parent_section = kwargs.get('parent_section', None)

        # 字章节
        self.child_sections = []

    def insert_new_row(self):
        # 计算综合排序
        self.section_order = self._cal_section_order()
        super(SectionBaseStore, self).insert_new_row()

    def __repr__(self):
        return '<id:{},name:{},summary:{}'.format(self.id, self.name, self.summary)

    def _cal_section_order(self):
        """计算SectionOrder"""
        if self.level == 0 or self.order_num == 0:
            raise Exception('先确定level和order_num,再计算section_order')
        section_order = self.order_num * (1000 ** (3 - self.level))
        if self.parent_section:
            section_order += self.parent_section.section_order
        return section_order

    @classmethod
    def get_section_by_assist(cls, assist_id, level):
        sql = """
        SELECT * FROM base_course_section
        WHERE assist_id={} AND level={};
        """.format(assist_id, level)
        res = cls.select(sql)
        return [
            cls(
                id=d['section_id'],
                name=d['name'],
                summary=d['summary'],
                level=d['level'],
                parent_id=d['parent_id'],
                order_num=d['order_num'],
                section_order=d['section_order'],
                assist_id=d['assist_ids'],
                last=d['last']
            ) for d in res
        ]

    def insert_relate_section_question(self, question_id):
        if not self.id:
            raise Exception('Section没有id')
        """将关卡id和questions的id写入关联表"""
        fields = dict(
            section_id=self.id,
            question_id=question_id,
            assist_id=self.assist_id,
            status=0,
            online_status=1
        )
        sql = """
        INSERT INTO relate_section_question (section_id,question_id,assist_id,status,online_status)
        VALUES ({section_id},{question_id},{assist_id},{status},{online_status})
        """.format(**fields)
        self.insert(sql)


class SectionTreeStore(SectionBaseStore):
    def __init__(self, **kwargs):
        super(SectionTreeStore, self).__init__(**kwargs)

        # 获取章节树
        if self.level < 4:
            self.child_sections = self.get_child_sections()

    def get_child_sections(self):
        """用自身id作为parent_id找到子节点的列表"""
        if not self.id:
            raise Exception('section没有id')
        sql = """
        SELECT * FROM base_course_section
        WHERE parent_id={}
        """.format(self.id)
        res = self.select(sql)
        return [
            self.__class__(
                id=d['section_id'],
                name=d['name'],
                summary=d['summary'],
                level=d['level'],
                parent_id=d['parent_id'],
                order_num=d['order_num'],
                section_order=d['section_order'],
                assist_id=d['assist_ids'],
                last=d['last'],
                parent_section=self
            ) for d in res
        ]


class MissionStore(SectionBaseStore):
    def __init__(self, **kwargs):
        super(MissionStore, self).__init__(**kwargs)
        self.questions = []

    def write_relate_self_questions(self):
        if not self.id:
            raise Exception('题目没有id')
        for q in self.questions:
            self.insert_relate_section_question(q.id)


class AssistStore(BaseModel):
    """教辅"""

    def __init__(self, **kwargs):
        self.__tablename__ = 'base_assist'
        self.insert_dict = {
            'name': 'Name',
            'summary': 'summary',
            'book_id': 'book_id',
            'q_type': 'type',
            'online_status': 'online_status',
            'status': 'status',
        }

        self.id = IntegerField()
        self.name = StringField()
        self.summary = StringField()
        self.book_id = IntegerField()
        self.q_type = IntegerField()
        self.online_status = 1
        self.status = 0
        super(AssistStore, self).__init__(**kwargs)
