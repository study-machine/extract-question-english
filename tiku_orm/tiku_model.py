# coding=utf8
from tiku_orm.base_field import *
from tiku_orm.base_model import *
from random_questions.utils import *

class SectionBase(BaseModel):
    def __init__(self, **kwargs):
        self.__tablename__ = 'wx_edu_coursesection'
        self.insert_dict = {
            'name': 'SectionName',
            'summary': 'Summary',
            'level': 'sLevel',
            'parent_id': 'ParentID',
            'order_num': 'OrderNum',
            'book_id': 'JiaoCaiID',
            'section_order': 'SectionOrder',
            'assist_id': 'TeachingAssistID',
            'grade': 'Grade',
            'subject': 'Subject',
            'last': 'Last',
            'q_type': 'QuestionType',
        }
        self.id = IntegerField(column_name='CourseSectionID')  # SectionID
        self.name = StringField(column_name='SectionName')  # SectionName
        self.summary = StringField(column_name='Summary')
        self.level = IntegerField(column_name='sLevel')  # level
        self.parent_id = IntegerField(column_name='ParentID')
        self.order_num = IntegerField(column_name='OrderNum')  # 顺序
        self.book_id = IntegerField(column_name='JiaoCaiID')  # 教材_id
        self.section_order = IntegerField(column_name='SectionOrder')  # 综合顺序
        self.assist_id = IntegerField(column_name='TeachingAssistID')  # 教辅id
        self.grade = IntegerField(column_name='Grade')
        self.subject = IntegerField(column_name='Subject')  # 学科
        self.last = IntegerField(column_name='Last')
        self.q_type = IntegerField(column_name='QuestionType')  # 章节type21
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
        SELECT * FROM wx_edu_coursesection
        WHERE TeachingAssistID={} AND sLevel={};
        """.format(assist_id, level)
        res = cls.select(sql)
        return [
            cls(
                id=d['CourseSectionID'],
                name=d['SectionName'],
                summary=d['Summary'],
                level=d['sLevel'],
                parent_id=d['ParentID'],
                order_num=d['OrderNum'],
                book_id=d['JiaoCaiID'],
                section_order=d['SectionOrder'],
                assist_id=d['TeachingAssistID'],
                grade=d['Grade'],
                subject=d['Subject'],
                last=d['Last'],
                q_type=d['QuestionType']
            ) for d in res
        ]

    def insert_relate_section_question(self, question_id):
        if not self.id:
            raise Exception('Section没有id')
        """将关卡id和questions的id写入关联表"""
        fields = dict(
            CourseSectionID=self.id,
            QuestionID=question_id,
            TeachingAssistID=self.assist_id
        )
        sql = """
        INSERT INTO edu_relate_courseassistquestion (CourseSectionID,QuestionID,TeachingAssistID)
        VALUES ({CourseSectionID},{QuestionID},{TeachingAssistID})
        """.format(**fields)
        self.insert(sql)


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
        SELECT * FROM wx_edu_coursesection
        WHERE ParentID={}
        """.format(self.id)
        res = self.select(sql)
        return [
            self.__class__(
                id=d['CourseSectionID'],
                name=d['SectionName'],
                summary=d['Summary'],
                level=d['sLevel'],
                parent_id=d['ParentID'],
                order_num=d['OrderNum'],
                book_id=d['JiaoCaiID'],
                section_order=d['SectionOrder'],
                assist_id=d['TeachingAssistID'],
                grade=d['Grade'],
                subject=d['Subject'],
                last=d['Last'],
                q_type=d['QuestionType'],
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


class Edition(BaseModel):
    """教材版本"""

    def __init__(self, **kwargs):
        self.id = IntegerField()
        self.name = StringField()
        super(Edition, self).__init__(**kwargs)

    @classmethod
    def get_all_editions(cls):
        sql = """
        SELECT TeachingID,Name FROM wx_edu_teachingmaterial;
        """
        res = cls.select(sql)
        return [
            cls(
                id=d['TeachingID'],
                name=d['Name']
            )
            for d in res
        ]


class Book(BaseModel):
    """教材，含年级和分科信息"""

    def __init__(self, **kwargs):
        self.id = IntegerField()
        self.name = StringField()
        self.grade = IntegerField()
        self.subject = IntegerField()
        self.edition_id = IntegerField()
        super(Book, self).__init__(**kwargs)

    def __repr__(self):
        return '<{}-{}-{}年级>'.format(self.id, self.name, self.grade)

    @classmethod
    def get_all_books(cls, subject):
        """获取一个出版社的教材"""
        # IsActive 为可用教材
        sql = """
        SELECT JiaoCaiID,Name,Grade,Subject FROM wx_edu_jiaocai 
        where IsActive=1 and Subject={subject};
        """.format(subject=subject)
        res = cls.select(sql)
        return [
            cls(
                id=d['JiaoCaiID'],
                name=d['Name'],
                grade=d['Grade'],
                subject=subject
            ) for d in res
        ]


class Assist(BaseModel):
    """教辅"""

    def __init__(self, **kwargs):
        self.__tablename__ = 'wx_edu_teachingassist'
        self.insert_dict = {
            'name': 'Name',
            'summary': 'Summary',
            'book_id': 'JiaocaiID',
            'q_type': 'QuestionType',
            'grade': 'Grade',
            'subject': 'Subject',
        }

        self.id = IntegerField(column_name='TeachingAssistID')
        self.name = StringField(column_name='Name')
        self.summary = StringField(column_name='Summary')
        self.book_id = IntegerField(column_name='JiaocaiID')
        self.q_type = IntegerField(column_name='QuestionType')
        self.grade = IntegerField(column_name='Grade')
        self.subject = IntegerField(column_name='Subject')
        super(Assist, self).__init__(**kwargs)

    @classmethod
    def get_assist_by_book(cls, book_id):
        """根据教材id获得教辅，测试库的基础教辅为summary=小学英语基础"""
        sql = """
        SELECT * FROM wx_edu_teachingassist WHERE Summary='小学英语基础' AND JiaocaiID={}
        """.format(book_id)
        res = cls.select(sql)
        return [
            cls(
                id=d['TeachingAssistID'],
                name=d['Name'],
                summary=d['Summary'],
                book_id=d['JiaocaiID'],
                q_type=d['QuestionType'],
                grade=d['Grade'],
                subject=d['Subject']
            ) for d in res
        ]


class CategoryItem(BaseModel):
    """
    选题范围，即CategoryID为3的数据
        CategoryID为4的分类，直接放入常量
    group 字符串
    """

    def __init__(self, **kwargs):
        self.id = IntegerField()
        self.name = StringField()
        self.group = StringField()
        super(CategoryItem, self).__init__(**kwargs)

    def __repr__(self):
        return '<id:{},name:{},group:{}>'.format(self.id, self.name, self.group)

    def __eq__(self, other):
        if isinstance(other, Question):
            return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    @classmethod
    def get_categoryitem_by_coursesection(cls, section_id):
        """根据CourseSection找到关联的CategoryItem"""
        sql = """
        SELECT DISTINCT item.CategoryItemID,item.CategoryItem,item.Group
        FROM edu_relate_coursesectioncategory AS relate
        INNER JOIN edu_categoryitem AS item ON item.CategoryItemID = relate.CategoryItemID
        INNER JOIN wx_edu_coursesection AS sec ON sec.CourseSectionID = relate.CourseSectionID
        WHERE item.CategoryID = 3
        AND relate.CourseSectionID = {}
        """.format(section_id)
        res = cls.select(sql)
        return [cls(
            id=d['CategoryItemID'],
            name=d['CategoryItem'],
            group=d['Group']
        ) for d in res]


class Question(BaseModel):
    """题目"""

    def __init__(self, **kwargs):
        self.id = IntegerField()
        self.body = StringField()
        self.q_type = IntegerField()
        self.item_group = StringField()  # 音形义
        super(Question, self).__init__(**kwargs)

    def __eq__(self, other):
        if isinstance(other, Question):
            return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return '<id:{},group:{}>'.format(self.id, self.item_group)

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
        WHERE q.Status=0 AND c.CategoryID = 4 AND r1.CategoryItemID = {};
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
