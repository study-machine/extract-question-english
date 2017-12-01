# coding=utf8
import sys, os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)

from tiku_orm.tiku_model import *
from utils import *
from logger import get_logger

log = get_logger('run')


def cut_six_times(question_list):
    # 切掉不足6的倍数
    n = len(question_list) % 6
    if n != 0:
        question_list = question_list[:len(question_list) - n]
    return question_list


def assist_generator():
    all_book = Book.get_all_books(2)
    for book in all_book:
        assist_list = Assist.get_assist_by_book(book.id)
        for assist in assist_list:
            yield book, assist


class SectionTreeWorker(object):
    """章节树工作类"""

    def __init__(self, section_tree, assist):
        """
        :param section_tree:    章节树
        :param assist:          章节树所属教辅
        """
        self.section_tree = section_tree
        self.assist = assist
        self.new_assist = None  # 新教辅
        self.new_tree = None  # 新章节树，册开头
        self.recurse_section_tree(section_tree)

        for ce in self.new_tree.child_sections:
            mg = MissionGroupMaker(ce.ce_words + ce.ce_sentences, ce)
            for m in mg.missions:
                m.insert_new_row()
                m.write_relate_self_questions()

    def recurse_section_tree(self, section):
        """递归处理一棵章节树"""
        log.info('获取到章节:{}'.format(section))
        if section.level > 3:  # 4级章节 练习
            if section.name == '词汇':
                items = CategoryItem.get_categoryitem_by_coursesection(section.id)
                section.parent_section.parent_section.map_section.ce_words += items
            if section.name == '句型':
                items = CategoryItem.get_categoryitem_by_coursesection(section.id)
                section.parent_section.parent_section.map_section.ce_sentences += items
            return
        if section.level == 1:  # 册
            # 创建新教辅
            self.create_new_assist(section)
            self.create_new_section(section)
        elif section.level == 2:  # 单元
            self.create_new_section(section)
            # 新建单元下面的单词
            section.map_section.ce_words = []
            section.map_section.ce_sentences = []
        elif section.level == 3:  # 课程
            pass
        for child in section.child_sections:
            self.recurse_section_tree(child)

    def create_new_assist(self, section_ce):
        """基于<册>创建新教辅"""
        self.new_assist = Assist(
            name=section_ce.summary + '-英语同步练',
            summary='英语同步练',
            book_id=self.assist.book_id,
            q_type=122,  # 英语同步练122
            grade=self.assist.grade,
            subject=2  # 英语
        )
        self.new_assist.insert_new_row()
        log.info('Insert new 教辅:{}'.format(self.new_assist))

    def create_new_section(self, section):
        parent_id = 0
        parent_section = None
        if section.level == 2:  # 单元
            parent_id = section.parent_section.map_section.id
            parent_section = section.parent_section.map_section

        new_section = SectionBase(
            name=section.name,
            summary='英语同步练',
            level=section.level,
            parent_id=parent_id,
            order_num=1,
            book_id=self.new_assist.book_id,
            assist_id=self.new_assist.id,
            grade=self.assist.grade,
            subject=2,  # 英语
            last=0,
            q_type=25,  # 同步练 章节type 25
            parent_section=parent_section
        )
        new_section.insert_new_row()
        if new_section.level < 3:
            # map_section为基础章节的映射章节，及同步练章节
            section.map_section = new_section
        if new_section.level == 2:
            self.new_tree.child_sections.append(new_section)
        if section.level == 1:
            self.new_tree = new_section
        log.info('Insert new section:{}'.format(self.new_tree))


class MissionGroupMaker(object):
    def __init__(self, items, ce):
        self.items = items
        self.ce = ce
        self.confirm_questions = []
        # self.back_questions = []
        self.missions = []
        for item in self.items:
            self.extract_question(item.id)

        self.confirm_questions = cut_six_times(self.confirm_questions)
        self.product_missons()

    def product_missons(self):
        n = len(self.confirm_questions)
        if n < 6:
            raise Exception('单元题目小于6无法组成关卡')
        for i in xrange(n / 6):
            mission = Mission(
                name='第{}关'.format(i + 1),
                summary='英语同步练',
                level=3,
                parent_id=self.ce.id,
                order_num=i + 1,
                book_id=self.ce.book_id,
                assist_id=self.ce.assist_id,
                grade=self.ce.grade,
                subject=2,  # 英语
                last=1,
                q_type=25,  # 同步练 章节type 25
                parent_section=self.ce
            )
            mission.questions = self.confirm_questions[i * 6:i * 6 + 6]
            self.missions.append(mission)

    def extract_question(self, item_id):
        question_list = Question.get_questions_by_item(item_id)
        need = {'音': 0,
                '形': 0,
                '义': 0}
        for question in question_list:
            if question.item_group == '音':
                if not need['音']:
                    self.extract_confirm_questions(question_list)
                    need['音'] += 1
            if question.item_group == '形':
                if not need['形']:
                    self.extract_confirm_questions(question_list)
                    need['形'] += 1
            if question.item_group == '义':
                if not need['义']:
                    self.extract_confirm_questions(question_list)
                    need['义'] += 1

    def extract_confirm_questions(self, questions):
        q = pop_random_question(questions)
        if not q or q.id in {q.id for q in self.confirm_questions}:
            q = pop_random_question(questions)
        self.confirm_questions.append(q)
        return True

    @staticmethod
    def pop_random_question(questions):
        """选随机题目"""
        if questions:
            return questions.pop(randint(0, len(questions) - 1))


def run():
    for book, assist in assist_generator():
        log.info('获得教材下:<{}>的教辅:<{}>'.format(book, assist))

        st_list = SectionTree.get_section_by_assist(assist_id=assist.id, level=1)
        for st in st_list:
            # 处理章节树
            SectionTreeWorker(st, assist)


if __name__ == '__main__':
    log.info('开始')
    run()
    log.info('结束')
