# coding=utf-8

import base64
import json
import sys
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.parse import quote_plus, urlencode
import os
from .. import config, constants, logging, Conversation

timer = time.perf_counter
CUID = constants.mac_id
logger = logging.getLogger(__name__)


class DemoError(Exception):
    pass


"""  ASR_TOKEN start """


def ASR_fetch_token(API_KEY, SECRET_KEY, SCOPE):
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)

    post_data = post_data.encode('utf-8')
    req = Request(constants.Baidu_tts_TOKEN_URL, post_data)
    try:
        f = urlopen(req)
        result_str = f.read()
    except HTTPError as err:
        logger.error('token http response http code : ' + str(err.code))
        result_str = err.read()
    result_str = result_str.decode()

    result = json.loads(result_str)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        # SCOPE = False 忽略检查
        if SCOPE and (not SCOPE in result['scope'].split(' ')):
            raise DemoError('scope is not correct')
        logger.debug('SUCCESS WITH TOKEN: %s  EXPIRES IN SECONDS: %s' %
                     (result['access_token'], result['expires_in']))
        return result['access_token']
    else:
        raise DemoError(
            'MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')


"""  ASR_TOKEN end """


def transcribe(fpath, API_KEY, apiscret, DEV_PID):
    if DEV_PID == 80001:
        # 极速版
        DEV_PID = 80001
        ASR_URL = 'http://vop.baidu.com/pro_api'
        SCOPE = 'brain_enhanced_asr'  # 有此scope表示有极速版能力，没有请在网页里开通极速版
    else:
        # 普通版
        DEV_PID = 1537  # 1537 表示识别普通话，使用输入法模型。根据文档填写PID，选择语言及识别模型
        ASR_URL = 'http://vop.baidu.com/server_api'
        SCOPE = 'audio_voice_assistant_get'  # 有此scope表示有asr能力，没有请在网页里勾选，非常旧的应用可能没有

    # 测试自训练平台需要打开以下信息， 自训练平台模型上线后，您会看见 第二步：“”获取专属模型参数pid:8001，modelid:1234”，按照这个信息获取 dev_pid=8001，lm_id=1234
    # DEV_PID = 8001 ;
    # LM_ID = 1234 ;

    # 忽略scope检查，非常旧的应用可能没有
    # SCOPE = False

    # 采样率
    RATE = 16000  # 固定值

    AUDIO_FILE = fpath
    print(fpath)
    FORMAT = AUDIO_FILE[-3:]
    token = ASR_fetch_token(API_KEY, apiscret, SCOPE)

    speech_data = []
    with open(AUDIO_FILE, 'rb') as speech_file:
        speech_data = speech_file.read()

    length = len(speech_data)
    if length == 0:
        raise DemoError('file %s length read 0 bytes' % AUDIO_FILE)
    speech = base64.b64encode(speech_data)

    speech = str(speech, 'utf-8')
    params = {'dev_pid': DEV_PID,
              # "lm_id" : LM_ID,    #测试自训练平台开启此项
              'format': FORMAT,
              'rate': RATE,
              'token': token,
              'cuid': CUID,
              'channel': 1,
              'speech': speech,
              'len': length
              }
    post_data = json.dumps(params, sort_keys=False)
    req = Request(ASR_URL, post_data.encode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    try:
        begin = timer()
        f = urlopen(req)
        result_str = f.read()
        logger.debug("Request time cost %f" % (timer() - begin))
    except HTTPError as err:
        logger.debug('asr http response http code : ' + str(err.code))
        result_str = err.read()

    result_str = str(result_str, 'utf-8')
    b = json.loads(result_str)
    logger.debug(b)
    if (b['err_no']) == 0:

        logger.info(b)

        return ''.join(b['result'])

    else:
        logger.error(b['err_no'])
        return ''


"""  TTS_TOKEN start """


def TTS_fetch_token(api_key, secret_key):
    logger.debug("fetch token begin")
    params = {'grant_type': 'client_credentials',
              'client_id': api_key, 'client_secret': secret_key}
    post_data = urlencode(params)
    post_data = post_data.encode('utf-8')
    req = Request(constants.Baidu_tts_TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except HTTPError as err:
        logger.error('token http response http code : ' + str(err.code))
        result_str = err.read()
    result_str = result_str.decode()
    # logger.debug(result_str)
    result = json.loads(result_str)
    # logger.debug(result)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not constants.Baidu_tts_SCOPE in result['scope'].split(' '):
            raise DemoError('scope is not correct')
        #logger.debug('SUCCESS WITH TOKEN: %s ; EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['access_token']
    else:
        raise DemoError(
            'MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')


"""  TTS_TOKEN end """

<<<<<<< HEAD
def get_speech(api_key,secret_key,TEXT,PER,SPD,PIT,VOL,AUE,TTS_URL,FORMAT):
    token = TTS_fetch_token(api_key,secret_key)
=======

def get_speech(api_key, secret_key, TEXT, PER, SPD, PIT, VOL, AUE, TTS_URL, FORMAT):
    token = TTS_fetch_token(api_key, secret_key)
>>>>>>> 6095ebb181ac71d27cfa62e9c3aafc05af796ef9
    tex = quote_plus(TEXT)  # 此处TEXT需要两次urlencode
    logger.debug(tex)
    params = {'tok': token, 'tex': tex, 'per': PER, 'spd': SPD, 'pit': PIT, 'vol': VOL, 'aue': AUE, 'cuid': CUID,
              'lan': 'zh', 'ctp': 1}  # lan ctp 固定参数

    data = urlencode(params)
    #logger.debug('test on Web Browser' + TTS_URL + '?' + data)

    req = Request(TTS_URL, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()

        headers = dict((name.lower(), value)
                       for name, value in f.headers.items())

        has_error = ('content-type' not in headers.keys()
                     or headers['content-type'].find('audio/') < 0)
    except HTTPError as err:
        logger.debug('asr http response http code : ' + str(err.code))
        result_str = err.read()
        has_error = True

    save_file = "error.txt" if has_error else 'result.' + FORMAT
    with open(save_file, 'wb') as of:
        of.write(result_str)

    if has_error:
        result_str = str(result_str, 'utf-8')
        logger.debug("tts api  error:" + result_str)
    if os.path.exists('result.mp3'):
        return 'result.mp3'
    else:
        logger.error('合成语音出错')

    logger.debug("result saved as :" + save_file)
