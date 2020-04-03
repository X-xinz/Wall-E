import shelve
import time
import datetime
import os
from robot import logging, constants
logger = logging.getLogger(__name__)


def Base():
    s = shelve.open(constants.NEWDB_PATH)
    try:
        s['keyword'] = {'Mon': 0, 'Tue': 0, 'Wed': 0, 'Thu': 0,'Fri': 0, 'Sat': 0, 'Sun': 0, 'date': '1999-02-14'}
        s['TTS'] = {'Mon': 0, 'Tue': 0, 'Wed': 0, 'Thu': 0, 'Fri': 0, 'Sat': 0, 'Sun': 0, 'date': '1999-02-14'}
        s['ASR'] = {'Mon': 0, 'Tue': 0, 'Wed': 0, 'Thu': 0, 'Fri': 0, 'Sat': 0, 'Sun': 0, 'date': '1999-02-14'}
        s['robot'] = {'Mon': 0, 'Tue': 0, 'Wed': 0, 'Thu': 0, 'Fri': 0, 'Sat': 0, 'Sun': 0, 'date': '1999-02-14'}
        s['plugs'] = {'Mon': 0, 'Tue': 0, 'Wed': 0, 'Thu': 0, 'Fri': 0, 'Sat': 0, 'Sun': 0, 'date': '1999-02-14'}
    finally:
        s.close()


def utils(f, name, week):
    date = {'Mon': 0, 'Tue': 1, 'Wed': 2,
            'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}
    daynow = (datetime.datetime.now())
    dd = f[name]['date']
    dayold = datetime.datetime.strptime(str(dd), '%Y-%m-%d')
    days = (daynow-dayold).days
    if days != date[week]:
        adays = date[week]
        delta = datetime.timedelta(adays)
        ndays = (daynow - delta).strftime('%Y-%m-%d')
        for na in ['keyword', 'TTS', 'ASR', 'robot', 'plugs']:
            if na in f.keys():
                f[na]["Mon"] = 0
                f[na]["Tue"] = 0
                f[na]["Wed"] = 0
                f[na]["Thu"] = 0
                f[na]["Fri"] = 0
                f[na]["Sat"] = 0
                f[na]["Sun"] = 0
                f[na]["date"] = ndays
                logger.info("本周{}统计初始化成功".format(na))

        else:
            logger.error('error')
    return True


def set(AUE):
    """
    统计对应环节的唤醒次数
    :param AUE: 对应唤醒的序号 
                0:"keyword", 
                1: "TTS", 
                2: "ASR", 
                3: "robot",
                5:"plugs"
    ：returns: 无返回值
    """
    names = {0: "keyword", 1: "TTS", 2: "ASR", 3: "robot", 5: "plugs"}
    name = names[AUE]
    week = time.strftime("%a", time.localtime())
    if not os.path.exists(constants.DB_PATH):
        Base()
    with shelve.open(constants.NEWDB_PATH,flag='w',writeback=True)as f:    	
        if f[name]:
            if utils(f, name, week):
                f[name][week] += 1
                logger.debug('检测到{} 被使用！'.format(name))
        else:
            logger.debug("唤醒次数统计失败")


def get_numb():
    """
    获取本周所有模块唤醒次数

    :returns: 返回本周所有唤醒次数，返回值为多维数组。
    """
    if not os.path.exists(constants.DB_PATH):
        Base()
    else:
        with shelve.open(constants.NEWDB_PATH) as f:
            k = (list(f["keyword"].values()))[0:7]
            tts = (list(f['TTS'].values()))[0:7]
            a = (list(f['ASR'].values()))[0:7]
            robot = (list(f['robot'].values()))[0:7]
            plugs = (list(f['plugs'].values()))[0:7]
            RESULT = (k, tts, a, robot, plugs)
            return RESULT
