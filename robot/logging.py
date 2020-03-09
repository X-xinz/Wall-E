# -*- coding:utf-8 -*-

import logging
import os
import subprocess
from logging.handlers import RotatingFileHandler
from robot import constants

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
def getLogger(name):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(filename)s - %(funcName)s - line %(lineno)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(name)
    logger.setLevel(constants.LOG)
    # 1MB = 1024 * 1024 bytes
    file_handler = RotatingFileHandler(os.path.join(constants.OUTFILES_PATH, 'wukong.log'), maxBytes=1024*1024,backupCount=5)
    file_handler.setFormatter(formatter)
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