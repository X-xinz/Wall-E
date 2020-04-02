# -*- coding:utf-8 -*-
from .sdk import XunfeiSpeech, Baiduspeech
from abc import ABCMeta, abstractmethod
from robot import config, logging
logger = logging.getLogger(__name__)


class AbstractASR(object):

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
    def transcribe(self, fp):
        pass


class XunfeiASR(AbstractASR):
    SLUG = 'xunfei-asr'

    def __init__(self, appid, apikey, apisecret, **arges):
        self.appid = appid
        self.apikey = apikey
        self.apisecret = apisecret

    @classmethod
    def get_config(cls):
        return config.get('/xunfei_API', {})

    def transcribe(self, fpath):
        '''
        科大讯飞asr
        '''
        return XunfeiSpeech.transcribe(fpath, self.appid, self.apikey, self.apisecret)


class BaiduASR(AbstractASR):

    SLUG = 'baidu-asr'

    def __init__(self, api_key, secret_key, DEV_PID, **arges):
        self.dev_pid = DEV_PID
        self.apikey = api_key
        self.apisecret = secret_key

    @classmethod
    def get_config(cls):
        return config.get('/baidu_asr', {})

    def transcribe(self, fpath):
        '''
        百度-asr
        '''
        return Baiduspeech.transcribe(fpath, self.apikey, self.apisecret, self.dev_pid)

def get_engine_by_slug(slug=None):
    if not slug or type(slug) is not str:
        raise TypeError("无效的 ASR slug '%s'", slug)
    selected_engines = list(filter(lambda engine: hasattr(engine, "SLUG") and
                                   engine.SLUG == slug, get_engines()))
    if len(selected_engines) == 0:
        raise ValueError("错误：找不到名为 {} 的 ASR 引擎".format(slug))
    else:
        if len(selected_engines) > 1:
            logger.warning("注意: 有多个 ASR 名称与指定的引擎名 {} 匹配").format(slug)
        engine = selected_engines[0]
        logger.info("使用 {} ASR 引擎".format(engine.SLUG))
        return engine.get_instance()


def get_engines():
    def get_subclasses(cls):
        subclasses = set()
        for subclass in cls.__subclasses__():  # 便利取类的所有子类
            subclasses.add(subclass)
            subclasses.update(get_subclasses(subclass))
        return subclasses
    return [engine for engine in
            list(get_subclasses(AbstractASR))
            if hasattr(engine, 'SLUG') and engine.SLUG]
