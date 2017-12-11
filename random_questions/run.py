# coding=utf8
import sys, os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(BASE_DIR)
reload(sys)
sys.setdefaultencoding('utf-8')

from datetime import datetime
import re
from tiku_orm.tiku_model import *
from tiku_orm.store_model import *
from utils import *
from logger import get_logger
from change_name import special_unit_name, english_num
from tiku_orm.config import write_type

log = get_logger('run')

# 需排除的复习单元
EXCLUDE_UNIT_NAME = ['Revision', 'Recycle', 'Review', 'REVISION']


def handle_unit_name(section):
    """处理单元名"""
    # 特殊单元名称替换
    if section.id in special_unit_name:
        section.name = special_unit_name[section.id]
        return

    # 替换短名称
    pattern = '(Unit|UNIT|Module)\s(\d{1,2}|\w+).*'
    m = re.match(pattern, section.name)
    try:
        unit_num_str = m.group(2)
        try:
            unit_num_int = int(unit_num_str)
        except Exception:
            log.info('{} 是英语数字'.format(section.name))
            try:
                unit_num_int = english_num[unit_num_str.lower()]
            except:
                raise Exception('替换短名称有误')
        changed_name = 'Unit {}'.format(unit_num_int)
        log.info('{} 改为 {}'.format(section.name, changed_name))
        section.name = changed_name
    except Exception:
        pass


def filter_unit(unit_name):
    """排除单元"""
    for word in EXCLUDE_UNIT_NAME:
        pattern = '.*{}.*'.format(word)
        m = re.match(pattern, unit_name)
        if m:
            # 有包含筛选关键字的课程
            return 'drop'


def sort_by_item_group(question_list):
    """汉字题有排序需求，按照字音,字形,字义的顺序排列"""
    sort_value = {
        '音': 1,
        '义': 2,
        '形': 3,
    }
    try:
        res = sorted(question_list, key=lambda q: sort_value.get(q.item_group, 4))
    except Exception, e:
        log.critical(e)
        log.critical(question_list)
        raise
    return res


def cut_six_times(question_list):
    length = len(question_list)
    # 再去重一下
    question_list = list(set(question_list))
    if length != len(question_list):
        log.warning('抽的题里有重题，去重')
    # 大于8关，根据音义形截取多余的
    if len(question_list) > 48:
        log.info('题目数量超过48道题，只留8关')
        question_list = sort_by_item_group(question_list)
        question_list = question_list[:48]
    # 切掉不足6的倍数
    n = len(question_list) % 6
    if n != 0:
        log.info('题目数量为<{}>，截取后面的'.format(len(question_list)))
        question_list = question_list[:len(question_list) - n]
    return question_list


def assist_generator():
    all_book = Book.get_all_books(2)
    for book in all_book:
        assist_list = Assist.get_assist_by_book(book.id)
        for assist in assist_list:
            yield book, assist


NewSectionClass = SectionBase
NewAssistClass = Assist
NewMissionClass = Mission

if write_type == 'store':
    NewSectionClass = SectionBaseStore
    NewAssistClass = AssistStore
    NewMissionClass = MissionStore


class SectionTreeWorker(object):
    """章节树工作类"""

    def __init__(self, section_tree, assist, book):
        """
        :param section_tree:    章节树
        :param assist:          章节树所属教辅
        """

        self.section_tree = section_tree
        self.assist = assist  # 教辅
        self.book = book  # 教材
        self.new_assist = None  # 新教辅
        self.new_tree = None  # 新章节树，册开头
        self.recurse_section_tree(section_tree)
        self.write_unit_and_missions()

    def write_unit_and_missions(self):
        index = 1
        for unit in self.new_tree.child_sections:
            # 复习单元跳过
            if filter_unit(unit.name) == 'drop':
                log.warning('单元{}为复习章节，跳过'.format(unit))
                break
            items = list(set(unit.ce_words + unit.ce_sentences))
            mg = MissionGroupMaker(items, unit)
            if not mg.missions:
                log.error('单元的题目不足6到无法建立关卡'.format(unit))
                break
            unit.order_num = index
            unit.insert_new_row()
            log.info('Insert new 单元:{}'.format(unit))
            index += 1
            for m in mg.missions:
                m.parent_id = unit.id
                m.insert_new_row()
                log.info('Insert new 关卡:{}'.format(m))
                m.write_relate_self_questions()
                for q in m.questions:
                    log.debug('关卡题目包括:{}'.format(q))

    def recurse_section_tree(self, section):
        """递归处理一棵章节树"""
        log.debug('获取到章节:{}'.format(section))
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
            # 处理单元名称
            handle_unit_name(section)

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
        self.new_assist = NewAssistClass(
            name=section_ce.summary + '-英语同步练',
            summary='英语同步练',
            book_id=self.assist.book_id,
            q_type=122,  # 英语同步练122
            grade=self.book.grade,
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

        new_section = NewSectionClass(
            name=section.name,
            summary='' if section.level == 3 else '英语同步练',  # 关卡summary为空
            level=section.level,
            parent_id=parent_id,
            order_num=1,
            book_id=self.new_assist.book_id,
            assist_id=self.new_assist.id,
            grade=self.assist.grade,
            subject=2,  # 英语
            last=0,
            q_type=24,  # 同步练 章节type 21
            parent_section=parent_section
        )
        if section.level == 1:
            new_section.insert_new_row()
            log.info('Insert new 册:{}'.format(self.new_tree))
        if new_section.level < 3:
            # map_section为基础章节的映射章节，及同步练章节
            section.map_section = new_section
        if new_section.level == 2:
            self.new_tree.child_sections.append(new_section)
        if section.level == 1:
            self.new_tree = new_section


class MissionGroupMaker(object):
    def __init__(self, items, unit):
        self.items = items
        self.unit = unit
        self.confirm_questions = []
        # self.back_questions = []
        self.missions = []
        for item in self.items:
            self.extract_question(item.id)

        self.confirm_questions = cut_six_times(self.confirm_questions)
        self.product_missons()

    def product_missons(self):
        """创建关卡"""
        n = len(self.confirm_questions)
        if n < 6:
            return
        for i in xrange(n / 6):
            mission = NewMissionClass(
                name='第{}关'.format(i + 1),
                summary='',
                level=3,
                order_num=i + 1,
                book_id=self.unit.book_id,
                assist_id=self.unit.assist_id,
                grade=self.unit.grade,
                subject=2,  # 英语
                last=1,
                q_type=24,  # 同步练
                parent_section=self.unit
            )
            mission.questions = self.confirm_questions[i * 6:i * 6 + 6]
            self.missions.append(mission)

    def extract_question(self, item_id):
        question_list = Question.get_questions_by_item(item_id)
        need = {'音': 0,
                '形': 0,
                '义': 0}

        # item太少，多抽点题
        if len(self.items) < 5:
            log.warning('单元{}的item太少，多抽点题'.format(self.unit))
            for k in need:
                need[k] -= 1

            question_list = list(set(question_list))
        for question in question_list:
            if question.item_group == '音':
                if need['音'] < 1:
                    self.extract_confirm_questions(question_list)
                    need['音'] += 1
            if question.item_group == '形':
                if need['形'] < 1:
                    self.extract_confirm_questions(question_list)
                    need['形'] += 1
            if question.item_group == '义':
                if need['义'] < 1:
                    self.extract_confirm_questions(question_list)
                    need['义'] += 1

    def extract_confirm_questions(self, questions):
        if not questions:
            log.error('题目没了，{}题太少不够抽的'.format(self.unit))
            return
        q = pop_random_question(questions)
        if not q:
            return False
        if q or q.id in {q.id for q in self.confirm_questions}:
            q = pop_random_question(questions)
            if not q:
                return False
        log.debug('获取到题目:{}'.format(q))
        self.confirm_questions.append(q)
        return True

    @staticmethod
    def pop_random_question(questions):
        """选随机题目"""
        if not questions:
            log.warning('没有题可取了')
            return None
        if questions:
            return questions.pop(randint(0, len(questions) - 1))


def run():
    for book, assist in assist_generator():
        log.info('获得教材下:<{}>的教辅:<{}>'.format(book, assist))

        st_list = SectionTree.get_section_by_assist(assist_id=assist.id, level=1)
        for st in st_list:
            # 处理章节树
            SectionTreeWorker(st, assist, book)


if __name__ == '__main__':
    log.info('开始')
    start = datetime.now()
    run()
    end = datetime.now()
    log.info('结束,耗时:{}秒'.format((end - start).seconds))
