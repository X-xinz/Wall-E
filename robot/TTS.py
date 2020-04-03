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
from urllib.request import Request, urlopen
from wsgiref.handlers import format_date_time
from .sdk import XunfeiSpeech, Baiduspeech
import websocket
import yaml

import _thread as thread
from robot import Player, config, constants, logging
logger = logging.getLogger(__name__)


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

    def __init__(self, api_key, secret_key, PER, SPD, PIT, VOL, AUE, **args):
        self.TTS_URL = constants.Baidu_TTS_URL
        self.api_key = api_key
        self.secret_key = secret_key
        self.PER = PER
        self.SPD = SPD
        self.PIT = PIT
        self.VOL = VOL
        self.AUE = AUE
        FORMATS = {3: "mp3", 4: "pcm", 5: "pcm", 6: "wav"}
        self.FORMAT = FORMATS[self.AUE]

    @classmethod
    def get_config(cls):
        return config.get('/Baidu_tts', {})

    def get_speech(self,TEXT):
        return Baiduspeech.get_speech(self.api_key,self.secret_key,TEXT,self.PER,self.SPD,self.PIT,self.VOL,self.AUE,self.TTS_URL,self.FORMAT)


class XunFeiTTS(AbstractTTS):

    SLUG = 'xunfei-tts'

    def __init__(self, appid, apikey, apisecret, **args):
        self.appid = appid
        self.apikey = apikey
        self.apisecret = apisecret

    @classmethod
    def get_config(cls):
        return config.get('/xunfei_API', {})

    def get_speech(self, Text):
        return XunfeiSpeech.get_speech(Text,self.appid,self.apikey,self.apisecret)
    

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
