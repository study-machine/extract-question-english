# coding=utf8

#
# my config
#
from .others import get_upper_dir

# 项目根目录
BASE_DIR = get_upper_dir(__file__, 2)

if __name__ == '__main__':
    print(BASE_DIR)
