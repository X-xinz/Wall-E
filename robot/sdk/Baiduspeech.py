# coding=utf-8

import base64
import json
import sys
import time
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .. import config, constants, logging

timer = time.perf_counter

logger = logging.getLogger(__name__)
class DemoError(Exception):
    pass
"""  TOKEN start """
def fetch_token(API_KEY,SECRET_KEY,SCOPE):
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    
    post_data = post_data.encode( 'utf-8')
    req = Request(constants.Baidu_tts_TOKEN_URL, post_data)
    try:
        f = urlopen(req)
        result_str = f.read()
    except HTTPError as err:
        print('token http response http code : ' + str(err.code))
        result_str = err.read()
    
    result_str =  result_str.decode()

    print(result_str)
    result = json.loads(result_str)
    print(result)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        print(SCOPE)
        if SCOPE and (not SCOPE in result['scope'].split(' ')):  # SCOPE = False 忽略检查
            raise DemoError('scope is not correct')
        print('SUCCESS WITH TOKEN: %s  EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['access_token']
    else:
        raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')

"""  TOKEN end """

def transcribe(fpath,API_KEY,apiscret,DEV_PID):
    if DEV_PID==80001:
        # 极速版 
        DEV_PID = 80001
        ASR_URL = 'http://vop.baidu.com/pro_api'
        SCOPE = 'brain_enhanced_asr'  # 有此scope表示有极速版能力，没有请在网页里开通极速版
    else:
        # 普通版
        DEV_PID = 1537  # 1537 表示识别普通话，使用输入法模型。根据文档填写PID，选择语言及识别模型
        ASR_URL = 'http://vop.baidu.com/server_api'
        SCOPE = 'audio_voice_assistant_get'  # 有此scope表示有asr能力，没有请在网页里勾选，非常旧的应用可能没有

    
    #测试自训练平台需要打开以下信息， 自训练平台模型上线后，您会看见 第二步：“”获取专属模型参数pid:8001，modelid:1234”，按照这个信息获取 dev_pid=8001，lm_id=1234
    # DEV_PID = 8001 ;   
    # LM_ID = 1234 ;
    
    # 忽略scope检查，非常旧的应用可能没有
    # SCOPE = False

    CUID = constants.mac_id
    # 采样率
    RATE = 16000  # 固定值

    AUDIO_FILE = fpath
    FORMAT = AUDIO_FILE[-3:]
    token = fetch_token(API_KEY,apiscret,SCOPE)

    speech_data = []
    with open(AUDIO_FILE, 'rb') as speech_file:
        speech_data = speech_file.read()

    length = len(speech_data)
    if length == 0:
        raise DemoError('file %s length read 0 bytes' % AUDIO_FILE)
    speech = base64.b64encode(speech_data)
    
    speech = str(speech, 'utf-8')
    params = {'dev_pid': DEV_PID,
             #"lm_id" : LM_ID,    #测试自训练平台开启此项
              'format': FORMAT,
              'rate': RATE,
              'token': token,
              'cuid': CUID,
              'channel': 1,
              'speech': speech,
              'len': length
              }
    post_data = json.dumps(params, sort_keys=False)
    # print post_data
    req = Request(ASR_URL, post_data.encode('utf-8'))
    req.add_header('Content-Type', 'application/json')
    try:
        begin = timer()
        f = urlopen(req)
        result_str = f.read()
        print ("Request time cost %f" % (timer() - begin))
    except HTTPError as err:
        print('asr http response http code : ' + str(err.code))
        result_str = err.read()
   
    result_str = str(result_str, 'utf-8')
    b = json.loads(result_str)
    logger.debug(b)    
    return((b['result'][0]))
