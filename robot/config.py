# -*-coding=utf-8 -*-

import yaml
import os
from robot import constants, logging

logger = logging.getLogger(__name__)


_config = {}
has_init = False


def init():
    global _config, has_init
    with open(constants.CONFIG_PATH, 'r') as f:
        _config = yaml.safe_load(f)
    has_init = True


def get_path(items, default=None):
    global _config
    curConfig = _config
    if isinstance(items, str) and items[0] == '/':
        items = items.split('/')[1:]
    for key in items:
        if key in curConfig:
            curConfig = curConfig[key]
        else:
            logger.warning('没有找到配置{},使用默认值{}'.format('/'.join(items), default))
            return default
    return curConfig


def has_path(items):
    global _config
    curConfig = _config
    if isinstance(items, str) and items[0] == '/':
        items = items.split('/')[1:]
    for key in items:
        if key in curConfig:
            curConfig = curConfig[key]
        else:
            return False
    return True


def get(item, default=None):
    """
    获取某个配置

    :param items:配置项名。若多级配置，则以'/a/b'或['a','b']形式
    :param default::默认值（可选）
    :return:返回配置值，无则返回一个默认值
    """
    global _config, has_init
    if not has_init:
        init()
    if not item:
        return _config
    return get_path(item, default)


def has(item):
    """
    判断是否有某个配置

    :param item:配置项名。若多级配置，则以'/a/b'或['a','b']形式
    :return:返回是否有配置
    """
    global _config, has_init
    if not has_init:
        init()
    return has_path(item)


def getText():
    """
    获取配置文本内容

    :returns:配置文件的文本内容    
    """
    if os.path.exists(constants.getConfigPath()):
        with open(constants.getConfigPath(), 'r') as f:
            return f.read()
    else:
        logger.error("配置文件不存在！")
        return ''


def dump(confihgStr):
    """
    将配置字符串写回配置文件
    :param configStr: 配置字符串
    """
    with open(constants.getConfigPath(), 'w') as f:
        f.write(confihgStr)
