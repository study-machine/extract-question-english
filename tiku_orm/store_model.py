# coding=utf8
from tiku_orm.base_field import *
from tiku_orm.base_model import *
from random_questions.utils import *

#
# 题库总库knowboxstore模型
#


class SectionBase(BaseModel):
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
        # question_type 暂时没有
        super(SectionBase, self).__init__(**kwargs)

        self.parent_section = kwargs.get('parent_section', None)

        # 字章节
        self.child_sections = []

    def insert_new_row(self):
        # 计算综合排序
        self.section_order = self._cal_section_order()
        super(SectionBase, self).insert_new_row()

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
            assist_id=self.assist_id
        )
        sql = """
        INSERT INTO relate_section_question (section_id,question_id,assist_id)
        VALUES ({section_id},{question_id},{assist_id})
        """.format(**fields)
        self.insert(sql)
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

    def get_relate_questions(self):
        """获取章节关联题目"""
        


class SectionTree(SectionBase):
    def __init__(self, **kwargs):
        super(SectionTree, self).__init__(**kwargs)

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


class Mission(SectionBase):
    def __init__(self, **kwargs):
        super(Mission, self).__init__(**kwargs)
        self.questions = []

    def write_relate_self_questions(self):
        if not self.id:
            raise Exception('题目没有id')
        for q in self.questions:
            self.insert_relate_section_question(q.id)


class Question(BaseModel):
    """题目"""

    def __init__(self, **kwargs):
        self.id = IntegerField()
        self.question = StringField()
        self.show_type = IntegerField()
        super(Question, self).__init__(**kwargs)

    def __eq__(self, other):
        if isinstance(other, Question):
            return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<id:{},question:{}>'.format(self.id, self.question)

    @classmethod
    def get_questions_by_item(cls, item_id):
        """
        根据CourseSection找到关联的CategoryItem
        本次要求填空题,Question表的QuestionType=1
        """
        sql = """
        SELECT q.QuestionID,q.Question,q.QuestionType,c.Group FROM wx_edu_questions_new AS q
        INNER JOIN edu_relate_questioncategory AS r1 ON q.QuestionID = r1.QuestionID
        INNER JOIN edu_relate_questioncategory AS r2 ON q.QuestionID = r2.QuestionID
        INNER JOIN edu_categoryitem AS c ON r2.CategoryItemID = c.CategoryItemID
        AND c.CategoryID = 4 WHERE r1.CategoryItemID = {}
        """.format(item_id)
        res = cls.select(sql)
        return [
            cls(
                id=d['QuestionID'],
                body=d['Question'],
                q_type=d['QuestionType'],
                item_group=d['Group']
            )
            for d in res
        ]
