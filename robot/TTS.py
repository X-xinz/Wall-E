# coding=utf-8
import base64
import datetime
import hashlib
import hmac
import json
import os
import ssl
import sys
import time
from abc import ABCMeta, abstractmethod
from datetime import datetime
from time import mktime
from urllib.error import HTTPError
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen
from wsgiref.handlers import format_date_time
from .sdk import XunfeiSpeech
import websocket
import yaml

import _thread as thread
from robot import Player, config, constants, logging




"""
baidu-tts
"""

class DemoError(Exception):
    pass
"""  TOKEN start """
logger = logging.getLogger(__name__)
class BDml(object):
    def fetch_token(self):        
        logger.debug("fetch token begin")
        params = {'grant_type': 'client_credentials',
                'client_id': config.get('/Baidu_tts/api_key',constants.Baidu_tts_apikey),
                'client_secret':config.get('/Baidu_tts/secret_key',constants.Baidu_tts_secret_key)}
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
        #logger.debug(result_str)
        result = json.loads(result_str)
        #logger.debug(result)
        if ('access_token' in result.keys() and 'scope' in result.keys()):
            if not constants.Baidu_tts_SCOPE in result['scope'].split(' '):
                raise DemoError('scope is not correct')
            #logger.debug('SUCCESS WITH TOKEN: %s ; EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
            return result['access_token']
        else:
            raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')
"""  TOKEN end """





class AbstractTTS(object):
    __metaclass__ = ABCMeta
    @classmethod
    def get_config(cls):
        return {}

    @classmethod
    def get_instance(cls):
        profile = cls.get_config()
        instance = cls(**profile)
        return instance

    @abstractmethod
    def get_speech(self, phrase):
        pass


class BaiduTTS(AbstractTTS):

    SLUG = 'baidu-tts'

    
    def __init__(self, PER, SPD,PIT,VOL,AUE,**args):
        self.TTS_URL = constants.Baidu_TTS_URL
        self.CUID = constants.get_mac          
        self.PER = PER                   
        self.SPD = SPD                    
        self.PIT = PIT                 
        self.VOL = VOL                  
        self.AUE = AUE                     
        FORMATS = {3: "mp3", 4: "pcm", 5: "pcm", 6: "wav"}
        self.FORMAT = FORMATS[self.AUE]

    @classmethod
    def get_config(cls):
        return config.get('/Baidu_tts',{})


    def get_speach(self,TEXT):
        token = BDml.fetch_token(self)
        tex = quote_plus(TEXT)  # 此处TEXT需要两次urlencode
        logger.debug(tex)
        params = {'tok': token, 'tex': tex, 'per': self.PER, 'spd': self.SPD, 'pit': self.PIT, 'vol': self.VOL, 'aue': self.AUE, 'cuid': self.CUID,
                'lan': 'zh', 'ctp': 1}  # lan ctp 固定参数

        data = urlencode(params)
        #logger.debug('test on Web Browser' + TTS_URL + '?' + data)

        req = Request(self.TTS_URL, data.encode('utf-8'))
        has_error = False
        try:
            f = urlopen(req)
            result_str = f.read()

            headers = dict((name.lower(), value) for name, value in f.headers.items())

            has_error = ('content-type' not in headers.keys() or headers['content-type'].find('audio/') < 0)
        except  HTTPError as err:
            logger.debug('asr http response http code : ' + str(err.code))
            result_str = err.read()
            has_error = True

        save_file = "error.txt" if has_error else 'result.' + self.FORMAT
        with open(save_file, 'wb') as of:
            of.write(result_str)

        if has_error:            
            result_str = str(result_str, 'utf-8')
            logger.debug("tts api  error:" + result_str)
        if os.path.exists('result.mp3'):
            return 'result.mp3'
        else:
            logger.error('合成语音出错')

        #logger.debug("result saved as :" + save_file)

class XunFeiTTS(AbstractTTS):

    SLUG = 'xunfei-tts'

    def __init__(self,appid,apikey,apisecret,**args):
        self.appid = appid
        self.apikey = apikey
        self.apisecret = apisecret
    
    @classmethod
    def get_config(cls):
        return config.get('/xunfei_API',{})

    def get_speach(self,Text):

        return XunfeiSpeech.get_speach(Text,self.appid,self.apikey,self.apisecret)
    

def get_engine_by_slug(slug=None):
    """
    Returns:
        A TTS Engine implementation available on the current platform

    Raises:
        ValueError if no speaker implementation is supported on this platform
    """

    if not slug or type(slug) is not str:
        raise TypeError("无效的 TTS slug '%s'", slug)

    selected_engines = list(filter(lambda engine: hasattr(engine, "SLUG") and
                              engine.SLUG == slug, get_engines()))

    if len(selected_engines) == 0:
        raise ValueError("错误：找不到名为 {} 的 TTS 引擎".format(slug))
    else:
        if len(selected_engines) > 1:
            logger.warning("注意: 有多个 TTS 名称与指定的引擎名 {} 匹配").format(slug)        
        engine = selected_engines[0]
        logger.info("使用 {} TTS 引擎".format(engine.SLUG))
        return engine.get_instance()


def get_engines():
    def get_subclasses(cls):
        subclasses = set()
        for subclass in cls.__subclasses__():
            subclasses.add(subclass)
            subclasses.update(get_subclasses(subclass))
        return subclasses
    return [engine for engine in
            list(get_subclasses(AbstractTTS))
            if hasattr(engine, 'SLUG') and engine.SLUG]
