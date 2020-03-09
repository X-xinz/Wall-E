# -*- coding:utf-8 -*-
from abc import ABCMeta, abstractmethod
import websocket
import datetime
import hashlib
import base64
import hmac
import json
import yaml
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
from robot import config,logging

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识

wsParam = None
gresult = ''
logger = logging.getLogger(__name__)



class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, AudioFile):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.AudioFile = AudioFile

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn",\
             "accent":"mandarin", "vinfo":1,"vad_eos":10000}

    # 生成url
    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
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
        # logger.debug("date: ",date)
        # logger.debug("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # logger.debug('websocket url :', url)
        return url


# 收到websocket消息的处理
def on_message(ws, message):
    global gresult
    try:
        code = json.loads(message)["code"]
        sid = json.loads(message)["sid"]
        if code != 0:
            errMsg = json.loads(message)["message"]
            logger.debug("sid:%s call error:%s code is:%s" % (sid, errMsg, code))

        else:
            data = json.loads(message)["data"]["result"]["ws"]
            # logger.debug(json.loads(message))
            result = ""
            for i in data:
                for w in i["cw"]:
                    result += w["w"]
            gresult = gresult + result
            #logger.debug("sid:%s call success!,data is:%s" % (sid, json.dumps(data, ensure_ascii=False)))
    except Exception as e:
        logger.debug("receive msg,but parse exception:%s"%(e))



# 收到websocket错误的处理
def on_error(ws, error):
    logger.debug("### error:%s"%(error))


# 收到websocket关闭的处理
def on_close(ws):
    pass
    #logger.debug("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws):
    global wsParam
    def run(*args):
        frameSize = 8000  # 每一帧的音频大小
        intervel = 0.04  # 发送音频间隔(单位:s)
        status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

        with open(wsParam.AudioFile, "rb") as fp:
            while True:
                buf = fp.read(frameSize)
                # 文件结束
                if not buf:
                    status = STATUS_LAST_FRAME
                # 第一帧处理
                # 发送第一帧音频，带business 参数
                # appid 必须带上，只需第一帧发送
                if status == STATUS_FIRST_FRAME:

                    d = {"common": wsParam.CommonArgs,
                         "business": wsParam.BusinessArgs,
                         "data": {"status": 0, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    d = json.dumps(d)
                    ws.send(d)
                    status = STATUS_CONTINUE_FRAME
                # 中间帧处理
                elif status == STATUS_CONTINUE_FRAME:
                    d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                # 最后一帧处理
                elif status == STATUS_LAST_FRAME:
                    d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                  "audio": str(base64.b64encode(buf), 'utf-8'),
                                  "encoding": "raw"}}
                    ws.send(json.dumps(d))
                    time.sleep(1)
                    break
                # 模拟音频采样间隔
                time.sleep(intervel)
        ws.close()

    thread.start_new_thread(run, ())
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

    SLUG='xunfei-asr'
    def __init__(self,appid,apikey,apisecret,**arges):
        self.appid=appid
        self.apikey=apikey
        self.apisecret=apisecret

    @classmethod
    def get_config(cls):
        return config.get('/xunfei_API',{})

    def transcribe(self,fpath):
        '''
        科大讯飞asr
        '''
        global wsParam
        global gresult
        gresult = ''
        time1 = datetime.now()
        wsParam = Ws_Param(APPID = self.appid,APIKey = self.apikey,APISecret=self.apisecret,AudioFile=fpath)
        websocket.enableTrace(False)
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
        ws.on_open = on_open
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        time2 = datetime.now()
        logger.debug(time2-time1)
        return gresult
def get_engine_by_slug(slug=None):
    """
    Returns:
        An ASR Engine implementation available on the current platform

    Raises:
        ValueError if no speaker implementation is supported on this platform
    """

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
        for subclass in cls.__subclasses__():           #便利取类的所有子类
            subclasses.add(subclass)
            subclasses.update(get_subclasses(subclass))
        return subclasses
    return [engine for engine in
            list(get_subclasses(AbstractASR))
            if hasattr(engine, 'SLUG') and engine.SLUG]