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

import websocket
import yaml

import _thread as thread
from robot import Player, config, constants, logging

from .utils import p_t_W


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




"""xunfei-tts"""





STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, apisecret, Text):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = apisecret
        self.Text = Text

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"aue": "raw", "auf": "audio/L16;rate=16000", "vcn": "x_xiaoshi_cts", "tte": "utf8","ent":"aisound","speed":45}
        self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-8')), "UTF8")}
        #使用小语种须使用以下方式，此处的unicode指的是 utf16小端的编码方式，即"UTF-16LE"”
        #self.Data = {"status": 2, "text": str(base64.b64encode(self.Text.encode('utf-16')), "UTF8")}

    # 生成url
    def create_url(self):
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/tts " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url
def on_message(ws, message):
    try:
        message =json.loads(message)
        code = message["code"]
        sid = message["sid"]
        audio = message["data"]["audio"]
        audio = base64.b64decode(audio)
        status = message["data"]["status"]
        #print(message)
        if status == 2:
            logger.debug("ws is closed")
            ws.close()
        if code != 0:
            errMsg = message["message"]
            logger.debug("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
        else:
            with open(constants.PCM_PATH, 'ab') as f:
                f.write(audio)
           
          

    except Exception as e:
        logger.error("receive msg,but parse exception:%s"%(e))



# 收到websocket错误的处理
def on_error(ws, error):
    logger.error("### error:%s"%(error))


# 收到websocket关闭的处理
def on_close(ws):
    print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws):
    def run(*args):
        d = {"common": wsParam.CommonArgs,
             "business": wsParam.BusinessArgs,
             "data": wsParam.Data,
             }
        d = json.dumps(d)
        logger.debug("------>开始发送文本数据")
        ws.send(d)
        if os.path.exists('./demo.pcm'):
            os.remove('./demo.pcm')

    thread.start_new_thread(run, ())






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
t=''
wsParam =()
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
        
        global wsParam,t
        t=Text
        wsParam = Ws_Param(APPID=self.appid, APIKey=self.apikey,
                        apisecret=self.apisecret,
                        Text=Text)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
        ws.on_open = on_open
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    
        
        p_t_W(constants.PCM_PATH)
        return constants.XUNFEITTS_PATH
    

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
