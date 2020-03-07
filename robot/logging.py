# -*- coding:utf-8 -*-

import logging
import subprocess
from logging import FileHandler
from robot import constants

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
def getLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(constants.LOG)
    file_handler = FileHandler(constants.LOGGING_PATH)
    logger.addHandler(file_handler)
    return logger


def readLog(lines = 200):
    """
    获取最新的指定行数的log

    :param lines:最大行数
    :returns:最新指定行数的log
    """
    res = subprocess.run(['tail','-n', str(lines), constants.LOGGING_PATH], 
                        cwd=constants.APP_PATH,
                        capture_output=True,
                        encoding="utf-8"
                        )

    return res.stdout